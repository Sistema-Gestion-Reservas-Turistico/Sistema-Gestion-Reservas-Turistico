from dataclasses import replace
from datetime import datetime, timedelta
from threading import Lock

from app.domain.entities.seguridad_login import (
    EstadoIntentosLogin,
    RegistroSeguridadLogin,
    TipoEventoSeguridadLogin,
)
from app.domain.interfaces.control_intentos_login import (
    ControlIntentosLoginRepository,
)


class InMemoryControlIntentosLoginRepository(ControlIntentosLoginRepository):
    def __init__(self) -> None:
        self._estados: dict[str, EstadoIntentosLogin] = {}
        self._eventos: list[RegistroSeguridadLogin] = []
        self._siguiente_evento_id = 1
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
            estado = self._obtener_o_crear_estado(correo_normalizado)
            estado = self._reiniciar_si_expirado(
                estado, fecha_hora, minutos_bloqueo
            )
            if estado.bloqueado_hasta is not None:
                return estado

            estado = replace(
                estado,
                intentos_fallidos=estado.intentos_fallidos + 1,
                ultimo_intento_en=fecha_hora,
            )
            self._estados[correo_normalizado] = estado
            self._registrar_evento_bajo_lock(
                correo_normalizado,
                "INTENTO_FALLIDO",
                fecha_hora,
                ip_origen,
                "Intento de inicio de sesión fallido",
            )
            if estado.intentos_fallidos >= max_intentos:
                hasta = fecha_hora + timedelta(minutes=minutos_bloqueo)
                estado = replace(estado, bloqueado_hasta=hasta)
                self._estados[correo_normalizado] = estado
                self._registrar_evento_bajo_lock(
                    correo_normalizado,
                    "BLOQUEO_CUENTA",
                    fecha_hora,
                    ip_origen,
                    "Cuenta bloqueada por intentos fallidos",
                )
            return estado

    def aplicar_bloqueo(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        bloqueado_hasta: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = self._obtener_o_crear_estado(correo_normalizado)
            if estado.bloqueado_hasta is not None:
                return estado
            estado = replace(
                estado,
                bloqueado_hasta=bloqueado_hasta,
                ultimo_intento_en=fecha_hora,
            )
            self._estados[correo_normalizado] = estado
            self._registrar_evento_bajo_lock(
                correo_normalizado,
                "BLOQUEO_CUENTA",
                fecha_hora,
                ip_origen,
                "Cuenta bloqueada por intentos fallidos",
            )
            return estado

    def levantar_bloqueo(
        self, correo_normalizado: str, fecha_hora: datetime
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = self._obtener_o_crear_estado(correo_normalizado)
            if (
                estado.bloqueado_hasta is not None
                and fecha_hora >= estado.bloqueado_hasta
            ):
                estado = self._reiniciar_estado(estado)
            return estado

    def reiniciar_contador(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        minutos_bloqueo: int,
        ip_origen: str | None = None,
    ) -> EstadoIntentosLogin:
        del ip_origen
        with self._lock:
            estado = self._obtener_o_crear_estado(correo_normalizado)
            expiro_sin_bloqueo = (
                estado.bloqueado_hasta is None
                and estado.intentos_fallidos > 0
                and estado.ultimo_intento_en is not None
                and fecha_hora - estado.ultimo_intento_en
                >= timedelta(minutes=minutos_bloqueo)
            )
            if expiro_sin_bloqueo:
                estado = self._reiniciar_estado(estado)
            return estado

    def marcar_notificacion_enviada(self, correo_normalizado: str) -> bool:
        with self._lock:
            estado = self._estados.get(correo_normalizado)
            if (
                estado is None
                or estado.bloqueado_hasta is None
                or estado.notificacion_enviada
            ):
                return False
            self._estados[correo_normalizado] = replace(
                estado, notificacion_enviada=True
            )
            return True

    def registrar_evento(
        self, evento: RegistroSeguridadLogin
    ) -> RegistroSeguridadLogin:
        with self._lock:
            return self._guardar_evento_bajo_lock(evento)

    def consultar_eventos(
        self, correo_normalizado: str
    ) -> list[RegistroSeguridadLogin]:
        with self._lock:
            return [
                evento
                for evento in self._eventos
                if evento.correo == correo_normalizado
            ]

    def registrar_login_exitoso(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        with self._lock:
            estado = self._obtener_o_crear_estado(correo_normalizado)
            estado = self._reiniciar_si_expirado(estado, fecha_hora, 0)
            if estado.bloqueado_hasta is not None:
                return estado

            estado = replace(
                estado,
                intentos_fallidos=0,
                ultimo_intento_en=None,
                bloqueado_hasta=None,
                notificacion_enviada=False,
            )
            self._estados[correo_normalizado] = estado
            self._registrar_evento_bajo_lock(
                correo_normalizado,
                "LOGIN_EXITOSO",
                fecha_hora,
                ip_origen,
                "Inicio de sesión con credenciales correctas",
            )
            return estado

    def _obtener_o_crear_estado(self, correo: str) -> EstadoIntentosLogin:
        estado = self._estados.get(correo)
        if estado is None:
            estado = EstadoIntentosLogin(correo_normalizado=correo)
            self._estados[correo] = estado
        return estado

    def _reiniciar_si_expirado(
        self,
        estado: EstadoIntentosLogin,
        ahora: datetime,
        minutos_bloqueo: int,
    ) -> EstadoIntentosLogin:
        bloqueo_expirado = (
            estado.bloqueado_hasta is not None
            and ahora >= estado.bloqueado_hasta
        )
        intentos_expirados = (
            estado.bloqueado_hasta is None
            and estado.intentos_fallidos > 0
            and estado.ultimo_intento_en is not None
            and minutos_bloqueo > 0
            and ahora - estado.ultimo_intento_en >= timedelta(minutes=minutos_bloqueo)
        )
        if bloqueo_expirado or intentos_expirados:
            estado = self._reiniciar_estado(estado)
        return estado

    def _reiniciar_estado(
        self, estado: EstadoIntentosLogin
    ) -> EstadoIntentosLogin:
        reiniciado = replace(
            estado,
            intentos_fallidos=0,
            ultimo_intento_en=None,
            bloqueado_hasta=None,
            notificacion_enviada=False,
        )
        self._estados[estado.correo_normalizado] = reiniciado
        return reiniciado

    def _registrar_evento_bajo_lock(
        self,
        correo: str,
        tipo_evento: TipoEventoSeguridadLogin,
        fecha_hora: datetime,
        ip_origen: str | None,
        detalle: str,
    ) -> RegistroSeguridadLogin:
        return self._guardar_evento_bajo_lock(
            RegistroSeguridadLogin(
                id=0,
                correo=correo,
                tipo_evento=tipo_evento,
                fecha_hora=fecha_hora,
                ip_origen=ip_origen,
                detalle=detalle,
            )
        )

    def _guardar_evento_bajo_lock(
        self, evento: RegistroSeguridadLogin
    ) -> RegistroSeguridadLogin:
        evento_guardado = replace(evento, id=self._siguiente_evento_id)
        self._eventos.append(evento_guardado)
        self._siguiente_evento_id += 1
        return evento_guardado
