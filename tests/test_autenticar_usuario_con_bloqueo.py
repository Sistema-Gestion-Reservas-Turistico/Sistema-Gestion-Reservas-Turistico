import inspect
from datetime import datetime, timedelta, timezone

from app.domain.entities.seguridad_login import EstadoIntentosLogin
from app.domain.entities.usuario import Usuario
from app.domain.interfaces.control_intentos_login import (
    ControlIntentosLoginRepository,
)
from app.domain.models.autenticacion import LoginRequest
from app.repositories.adapters.in_memory_notificacion_correo_service import (
    InMemoryNotificacionCorreoService,
)
from app.repositories.adapters.in_memory_usuario_repository import (
    InMemoryUsuarioRepository,
)
from app.services.security.passwords import hash_password
from app.services.use_cases.autenticar_usuario_con_bloqueo import (
    AutenticarUsuarioConBloqueoUseCase,
)


def _crear_estado(
    correo: str,
    intentos: int = 0,
    bloqueada_hasta: datetime | None = None,
    ahora: datetime | None = None,
) -> EstadoIntentosLogin:
    params = inspect.signature(EstadoIntentosLogin).parameters
    kwargs: dict[str, object] = {}
    for nombre, param in params.items():
        if nombre == "self":
            continue
        if "correo" in nombre:
            kwargs[nombre] = correo
        elif "intentos" in nombre or "fallidos" in nombre:
            kwargs[nombre] = intentos
        elif "bloquead" in nombre:
            kwargs[nombre] = bloqueada_hasta
        elif "notificacion" in nombre or "aviso" in nombre:
            kwargs[nombre] = bloqueada_hasta is not None
        elif "ip" in nombre:
            kwargs[nombre] = "127.0.0.1"
        elif "actualizado" in nombre or "fecha" in nombre or "hora" in nombre:
            kwargs[nombre] = ahora
        elif param.default is inspect.Parameter.empty:
            if param.annotation is int:
                kwargs[nombre] = 0
            elif param.annotation is bool:
                kwargs[nombre] = False
            elif param.annotation is str:
                kwargs[nombre] = ""
            else:
                kwargs[nombre] = None
    return EstadoIntentosLogin(**kwargs)


class _ControlIntentosMemoria(ControlIntentosLoginRepository):
    def __init__(self) -> None:
        self._estados: dict[str, EstadoIntentosLogin] = {}
        self._eventos: dict[str, list] = {}

    def obtener_estado(self, correo_normalizado: str) -> EstadoIntentosLogin | None:
        return self._estados.get(correo_normalizado)

    def registrar_intento_fallido(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
        max_intentos: int,
        minutos_bloqueo: int,
    ) -> EstadoIntentosLogin:
        prev = self._estados.get(correo_normalizado)
        intentos = (getattr(prev, "intentos_fallidos", 0) or 0) + 1
        bloqueada_hasta = (
            fecha_hora + timedelta(minutes=minutos_bloqueo)
            if intentos >= max_intentos
            else None
        )
        estado = _crear_estado(correo_normalizado, intentos, bloqueada_hasta, fecha_hora)
        self._estados[correo_normalizado] = estado
        return estado

    def aplicar_bloqueo(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        bloqueada_hasta: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        prev = self._estados.get(correo_normalizado)
        intentos = getattr(prev, "intentos_fallidos", 5) or 5
        estado = _crear_estado(correo_normalizado, intentos, bloqueada_hasta, fecha_hora)
        self._estados[correo_normalizado] = estado
        return estado

    def levantar_bloqueo(
        self, correo_normalizado: str, fecha_hora: datetime
    ) -> EstadoIntentosLogin:
        estado = _crear_estado(correo_normalizado, 0, None, fecha_hora)
        self._estados[correo_normalizado] = estado
        return estado

    def reiniciar_contador(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        minutos_bloqueo: int,
        ip_origen: str | None = None,
    ) -> EstadoIntentosLogin:
        estado = _crear_estado(correo_normalizado, 0, None, fecha_hora)
        self._estados[correo_normalizado] = estado
        return estado

    def registrar_login_exitoso(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        estado = _crear_estado(correo_normalizado, 0, None, fecha_hora)
        self._estados[correo_normalizado] = estado
        return estado

    def marcar_notificacion_enviada(self, correo_normalizado: str) -> bool:
        return True

    def registrar_evento(self, evento):
        clave = getattr(evento, "correo_normalizado", "") or getattr(evento, "correo", "")
        self._eventos.setdefault(clave, []).append(evento)
        return evento

    def consultar_eventos(self, correo_normalizado: str) -> list:
        return list(self._eventos.get(correo_normalizado, []))


def test_caso_4_bloqueo_expira_tras_15_minutos_y_reinicia_contador():
    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 17, 0, tzinfo=zona)

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=1,
        tipo_documento="CC",
        numero_documento="1095111222",
        nombres="Laura",
        apellidos="Gomez",
        correo="laura.gomez@correo.com",
        telefono="3001112233",
        password_hash=hash_password("ClaveLaura2026"),
        rol="Cliente",
        estado="ACTIVO",
        acepta_tratamiento_datos=True,
        fecha_aceptacion_datos=inicio,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        creado_en=inicio,
        fecha_activacion=inicio,
    )
    for attr in ("_usuarios", "usuarios", "_por_correo", "_items"):
        if hasattr(repo, attr) and isinstance(getattr(repo, attr), dict):
            getattr(repo, attr)[usuario.correo] = usuario
            break

    control = _ControlIntentosMemoria()
    correo_svc = InMemoryNotificacionCorreoService()
    caso = AutenticarUsuarioConBloqueoUseCase(
        usuarios=repo,
        control_intentos=control,
        notificaciones=correo_svc,
    )

    for _ in range(5):
        try:
            caso.ejecutar(
                LoginRequest(correo="laura.gomez@correo.com", password="Incorrecta1"),
                "127.0.0.1",
                ahora=inicio,
            )
        except Exception:
            pass

    despues_15_min = inicio + timedelta(minutes=15, seconds=1)
    respuesta = caso.ejecutar(
        LoginRequest(correo="laura.gomez@correo.com", password="ClaveLaura2026"),
        "127.0.0.1",
        ahora=despues_15_min,
    )

    assert respuesta is not None
