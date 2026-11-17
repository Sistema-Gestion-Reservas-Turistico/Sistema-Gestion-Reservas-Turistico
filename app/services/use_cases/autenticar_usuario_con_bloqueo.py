import logging
import math
from datetime import datetime, timedelta, timezone

from app.config import MAX_INTENTOS_FALLIDOS_LOGIN, MINUTOS_BLOQUEO_LOGIN
from app.domain.entities.seguridad_login import EstadoIntentosLogin
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.autenticacion import (
    CuentaBloqueadaTemporalmenteError,
    CuentaPendienteActivacionError,
    CredencialesInvalidasLoginError,
    PersistenciaSeguridadLoginError,
)
from app.domain.interfaces.control_intentos_login import (
    ControlIntentosLoginRepository,
)
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService
from app.domain.interfaces.usuarios import UsuarioRepository
from app.domain.models.autenticacion import LoginExitosoResponse, LoginRequest
from app.services.security.passwords import verify_password


_logger: logging.Logger = logging.getLogger(__name__)
_ZONA_HORARIA: timezone = timezone(timedelta(hours=-5), name="COT")


class AutenticarUsuarioConBloqueoUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        control_intentos: ControlIntentosLoginRepository,
        notificaciones: NotificacionCorreoService,
    ) -> None:
        self._usuarios = usuarios
        self._control_intentos = control_intentos
        self._notificaciones = notificaciones

    def ejecutar(
        self,
        solicitud: LoginRequest,
        ip_origen: str | None,
        ahora: datetime | None = None,
    ) -> LoginExitosoResponse:
        correo = solicitud.correo.strip().lower()
        momento = ahora or datetime.now(_ZONA_HORARIA)

        estado = self._consultar_estado(correo)
        estado = self._procesar_expiracion(correo, estado, momento, ip_origen)
        self._rechazar_si_bloqueado(estado, momento)

        try:
            usuario = self._usuarios.buscar_por_correo(correo)
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error

        credenciales_validas = usuario is not None and verify_password(
            solicitud.password, usuario.password_hash
        )
        if not credenciales_validas:
            estado = self._registrar_fallo(correo, momento, ip_origen)
            if estado.bloqueado_hasta is not None:
                self._notificar_bloqueo_si_corresponde(usuario, estado)
                self._rechazar_si_bloqueado(estado, momento)
            raise CredencialesInvalidasLoginError(
                max(0, MAX_INTENTOS_FALLIDOS_LOGIN - estado.intentos_fallidos)
            )

        estado = self._registrar_login_exitoso(correo, momento, ip_origen)
        self._rechazar_si_bloqueado(estado, momento)
        if usuario.estado not in {"ACTIVO", "ACTIVA"}:
            raise CuentaPendienteActivacionError()

        return LoginExitosoResponse(
            id=usuario.id,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            correo=usuario.correo,
            rol=usuario.rol,
        )

    def _consultar_estado(self, correo: str) -> EstadoIntentosLogin:
        try:
            return self._control_intentos.obtener_estado(correo) or EstadoIntentosLogin(
                correo_normalizado=correo
            )
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error

    def _procesar_expiracion(
        self,
        correo: str,
        estado: EstadoIntentosLogin,
        ahora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        bloqueo_expirado = (
            estado.bloqueado_hasta is not None and ahora >= estado.bloqueado_hasta
        )
        intentos_expirados = (
            estado.bloqueado_hasta is None
            and estado.intentos_fallidos > 0
            and estado.ultimo_intento_en is not None
            and ahora - estado.ultimo_intento_en
            >= timedelta(minutes=MINUTOS_BLOQUEO_LOGIN)
        )
        if not bloqueo_expirado and not intentos_expirados:
            return estado
        try:
            if bloqueo_expirado:
                return self._control_intentos.levantar_bloqueo(correo, ahora)
            return self._control_intentos.reiniciar_contador(
                correo, ahora, MINUTOS_BLOQUEO_LOGIN, ip_origen
            )
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error

    def _registrar_fallo(
        self,
        correo: str,
        ahora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        try:
            return self._control_intentos.registrar_intento_fallido(
                correo,
                ahora,
                ip_origen,
                MAX_INTENTOS_FALLIDOS_LOGIN,
                MINUTOS_BLOQUEO_LOGIN,
            )
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error

    def _registrar_login_exitoso(
        self,
        correo: str,
        ahora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        try:
            return self._control_intentos.registrar_login_exitoso(
                correo, ahora, ip_origen
            )
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error

    def _notificar_bloqueo_si_corresponde(
        self, usuario: Usuario | None, estado: EstadoIntentosLogin
    ) -> None:
        bloqueada_hasta = estado.bloqueado_hasta
        fecha_hora_bloqueo = estado.ultimo_intento_en
        if (
            usuario is None
            or bloqueada_hasta is None
            or fecha_hora_bloqueo is None
            or estado.notificacion_enviada
        ):
            return
        try:
            notificacion_reclamada = (
                self._control_intentos.marcar_notificacion_enviada(
                    estado.correo_normalizado
                )
            )
        except Exception as error:
            raise PersistenciaSeguridadLoginError() from error
        if not notificacion_reclamada:
            return
        try:
            self._notificaciones.enviar_aviso_bloqueo_cuenta(
                usuario, fecha_hora_bloqueo, bloqueada_hasta
            )
        except Exception:
            _logger.exception("No fue posible enviar el aviso de bloqueo de cuenta")

    @staticmethod
    def _rechazar_si_bloqueado(
        estado: EstadoIntentosLogin, ahora: datetime
    ) -> None:
        bloqueado_hasta = estado.bloqueado_hasta
        if bloqueado_hasta is None or ahora >= bloqueado_hasta:
            return
        segundos_restantes = (bloqueado_hasta - ahora).total_seconds()
        minutos_restantes = max(1, math.ceil(segundos_restantes / 60))
        raise CuentaBloqueadaTemporalmenteError(
            bloqueada_hasta=bloqueado_hasta,
            minutos_restantes=minutos_restantes,
        )
