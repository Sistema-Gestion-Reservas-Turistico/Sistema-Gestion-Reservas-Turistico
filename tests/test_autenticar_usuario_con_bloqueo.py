from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Lock

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


class _ControlIntentosMemoria(ControlIntentosLoginRepository):
    def __init__(self) -> None:
        self._estados: dict[str, EstadoIntentosLogin] = {}
        self._eventos: dict[str, list] = {}
        self._lock = Lock()

    def obtener_estado(self, correo_normalizado: str) -> EstadoIntentosLogin | None:
        with self._lock:
            return self._estados.get(correo_normalizado)

    def registrar_intento_fallido(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
        max_intentos: int,
        minutos_bloqueo: int,
    ) -> EstadoIntentosLogin:
        with self._lock:
            prev = self._estados.get(correo_normalizado)
            if prev is not None and prev.bloqueado_hasta is not None and fecha_hora < prev.bloqueado_hasta:
                return prev
            intentos = (prev.intentos_fallidos if prev is not None else 0) + 1
            bloqueado_hasta = (
                fecha_hora + timedelta(minutes=minutos_bloqueo)
                if intentos >= max_intentos
                else None
            )
            estado = EstadoIntentosLogin(
                correo_normalizado=correo_normalizado,
                intentos_fallidos=intentos,
                bloqueado_hasta=bloqueado_hasta,
                ultimo_intento_en=fecha_hora,
                notificacion_enviada=prev.notificacion_enviada if prev is not None else False,
            )
            self._estados[correo_normalizado] = estado
            return estado

    def aplicar_bloqueo(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        bloqueada_hasta: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        with self._lock:
            prev = self._estados.get(correo_normalizado)
            intentos = prev.intentos_fallidos if prev is not None else 5
            estado = EstadoIntentosLogin(
                correo_normalizado=correo_normalizado,
                intentos_fallidos=intentos,
                bloqueado_hasta=bloqueada_hasta,
                ultimo_intento_en=fecha_hora,
                notificacion_enviada=prev.notificacion_enviada if prev is not None else False,
            )
            self._estados[correo_normalizado] = estado
            return estado

    def levantar_bloqueo(
        self, correo_normalizado: str, fecha_hora: datetime
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = EstadoIntentosLogin(
                correo_normalizado=correo_normalizado,
                intentos_fallidos=0,
                bloqueado_hasta=None,
                ultimo_intento_en=fecha_hora,
                notificacion_enviada=False,
            )
            self._estados[correo_normalizado] = estado
            return estado

    def reiniciar_contador(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        minutos_bloqueo: int,
        ip_origen: str | None = None,
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = EstadoIntentosLogin(
                correo_normalizado=correo_normalizado,
                intentos_fallidos=0,
                bloqueado_hasta=None,
                ultimo_intento_en=fecha_hora,
                notificacion_enviada=False,
            )
            self._estados[correo_normalizado] = estado
            return estado

    def registrar_login_exitoso(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = EstadoIntentosLogin(
                correo_normalizado=correo_normalizado,
                intentos_fallidos=0,
                bloqueado_hasta=None,
                ultimo_intento_en=fecha_hora,
                notificacion_enviada=False,
            )
            self._estados[correo_normalizado] = estado
            return estado

    def marcar_notificacion_enviada(self, correo_normalizado: str) -> bool:
        with self._lock:
            prev = self._estados.get(correo_normalizado)
            if prev is None or prev.notificacion_enviada:
                return False
            self._estados[correo_normalizado] = EstadoIntentosLogin(
                correo_normalizado=prev.correo_normalizado,
                intentos_fallidos=prev.intentos_fallidos,
                bloqueado_hasta=prev.bloqueado_hasta,
                ultimo_intento_en=prev.ultimo_intento_en,
                notificacion_enviada=True,
            )
            return True

    def registrar_evento(self, evento):
        with self._lock:
            clave = getattr(evento, "correo_normalizado", "") or getattr(evento, "correo", "")
            self._eventos.setdefault(clave, []).append(evento)
            return evento

    def consultar_eventos(self, correo_normalizado: str) -> list:
        with self._lock:
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


def test_caso_10_intentos_simultaneos():
    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 18, 30, tzinfo=zona)

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=10,
        tipo_documento="CC",
        numero_documento="1095444555",
        nombres="Andres",
        apellidos="Rojas",
        correo="andres.rojas@correo.com",
        telefono="3004445566",
        password_hash=hash_password("ClaveAndres2026"),
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

    def _intentar_fallo(_: int):
        try:
            return caso.ejecutar(
                LoginRequest(correo="andres.rojas@correo.com", password="Incorrecta1"),
                "127.0.0.1",
                ahora=inicio,
            )
        except Exception as exc:
            return exc

    with ThreadPoolExecutor(max_workers=10) as pool:
        resultados = list(pool.map(_intentar_fallo, range(10)))

    assert len(resultados) == 10
    assert len(correo_svc.correos_enviados) == 1
    estado_final = control.obtener_estado("andres.rojas@correo.com")
    assert estado_final is not None
    assert estado_final.bloqueado_hasta is not None


def test_caso_11_falla_correo_aviso(caplog):
    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 19, 0, tzinfo=zona)

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=11,
        tipo_documento="CC",
        numero_documento="1095555666",
        nombres="Camila",
        apellidos="Vargas",
        correo="camila.vargas@correo.com",
        telefono="3005556677",
        password_hash=hash_password("ClaveCamila2026"),
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
    correo_svc.fallar_envio = True
    caso = AutenticarUsuarioConBloqueoUseCase(
        usuarios=repo,
        control_intentos=control,
        notificaciones=correo_svc,
    )

    excepciones = []
    for _ in range(5):
        try:
            caso.ejecutar(
                LoginRequest(correo="camila.vargas@correo.com", password="Incorrecta1"),
                "127.0.0.1",
                ahora=inicio,
            )
        except Exception as exc:
            excepciones.append(exc)

    estado = control.obtener_estado("camila.vargas@correo.com")
    assert estado is not None
    assert estado.bloqueado_hasta is not None
    assert len(correo_svc.correos_enviados) == 0
    assert len(excepciones) >= 1


def test_caso_12_valores_configurables(monkeypatch):
    import app.services.use_cases.autenticar_usuario_con_bloqueo as uc_mod

    monkeypatch.setattr(uc_mod, "MAX_INTENTOS_FALLIDOS_LOGIN", 3)
    monkeypatch.setattr(uc_mod, "MINUTOS_BLOQUEO_LOGIN", 5)

    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 19, 15, tzinfo=zona)

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=12,
        tipo_documento="CC",
        numero_documento="1095666777",
        nombres="Mateo",
        apellidos="Silva",
        correo="mateo.silva@correo.com",
        telefono="3006667788",
        password_hash=hash_password("ClaveMateo2026"),
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

    excepciones = []
    for _ in range(3):
        try:
            caso.ejecutar(
                LoginRequest(correo="mateo.silva@correo.com", password="Incorrecta1"),
                "127.0.0.1",
                ahora=inicio,
            )
        except Exception as exc:
            excepciones.append(exc)

    estado = control.obtener_estado("mateo.silva@correo.com")
    assert estado is not None
    assert estado.intentos_fallidos == 3
    assert estado.bloqueado_hasta == inicio + timedelta(minutes=5)
    assert any(getattr(e, "minutos_restantes", None) == 5 for e in excepciones)


def test_caso_13_registro_seguridad():
    from app.domain.entities.seguridad_login import RegistroSeguridadLogin

    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 19, 30, tzinfo=zona)
    ip_prueba = "192.168.1.50"
    correo_objetivo = "valentina.ruiz@correo.com"

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=13,
        tipo_documento="CC",
        numero_documento="1095777888",
        nombres="Valentina",
        apellidos="Ruiz",
        correo=correo_objetivo,
        telefono="3007778899",
        password_hash=hash_password("ClaveValentina2026"),
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

    for idx in range(5):
        instante = inicio + timedelta(seconds=idx * 5)
        try:
            caso.ejecutar(
                LoginRequest(correo=correo_objetivo, password="Incorrecta1"),
                ip_prueba,
                ahora=instante,
            )
        except Exception:
            pass
        estado_actual = control.obtener_estado(correo_objetivo)
        control.registrar_evento(
            RegistroSeguridadLogin(
                id=idx + 1,
                correo=correo_objetivo,
                tipo_evento=(
                    "BLOQUEO_CUENTA"
                    if estado_actual and estado_actual.bloqueado_hasta is not None
                    else "INTENTO_FALLIDO"
                ),
                fecha_hora=instante,
                ip_origen=ip_prueba,
                detalle=f"Intento #{idx + 1}",
            )
        )

    eventos = control.consultar_eventos(correo_objetivo)
    assert len(eventos) == 5
    assert any(ev.tipo_evento == "INTENTO_FALLIDO" for ev in eventos)
    assert any(ev.tipo_evento == "BLOQUEO_CUENTA" for ev in eventos)
    for ev in eventos:
        assert ev.correo == correo_objetivo
        assert ev.fecha_hora is not None
        assert ev.ip_origen == ip_prueba


def test_caso_14_no_se_puede_registrar_el_intento():
    from app.services.use_cases.autenticar_usuario_con_bloqueo import (
        PersistenciaSeguridadLoginError,
    )

    zona = timezone(timedelta(hours=-5), name="COT")
    inicio = datetime(2026, 11, 27, 19, 45, tzinfo=zona)
    correo_objetivo = "diego.morales@correo.com"
    clave_valida = "ClaveDiego2026"

    repo = InMemoryUsuarioRepository()
    usuario = Usuario(
        id=14,
        tipo_documento="CC",
        numero_documento="1095888999",
        nombres="Diego",
        apellidos="Morales",
        correo=correo_objetivo,
        telefono="3008889900",
        password_hash=hash_password(clave_valida),
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

    class _ControlFallaPersistencia(_ControlIntentosMemoria):
        def obtener_estado(self, correo_normalizado: str):
            raise RuntimeError("Fallo de conexión al consultar intentos")

    control = _ControlFallaPersistencia()
    correo_svc = InMemoryNotificacionCorreoService()
    caso = AutenticarUsuarioConBloqueoUseCase(
        usuarios=repo,
        control_intentos=control,
        notificaciones=correo_svc,
    )

    try:
        caso.ejecutar(
            LoginRequest(correo=correo_objetivo, password=clave_valida),
            "127.0.0.1",
            ahora=inicio,
        )
        assert False, "Debió lanzar PersistenciaSeguridadLoginError"
    except PersistenciaSeguridadLoginError as exc:
        assert "No fue posible iniciar sesión" in str(exc)
