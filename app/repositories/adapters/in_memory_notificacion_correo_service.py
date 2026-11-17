import logging
from dataclasses import dataclass
from datetime import datetime
from threading import Lock

from app.domain.entities.usuario import Usuario
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService


_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CorreoSeguridadEnviado:
    destinatario: str
    asunto: str
    cuerpo: str


class InMemoryNotificacionCorreoService(NotificacionCorreoService):
    def __init__(self) -> None:
        self.correos_enviados: list[CorreoSeguridadEnviado] = []
        self.fallar_envio = False
        self._lock = Lock()

    def enviar_enlace_activacion(
        self,
        correo: str,
        nombres: str,
        enlace_activacion: str,
        horas_vigencia: int,
    ) -> None:
        if self.fallar_envio:
            raise RuntimeError("No fue posible enviar el correo de activación")
        cuerpo = "\n".join(
            (
                f"Hola {nombres},",
                "Activa tu cuenta usando el siguiente enlace:",
                enlace_activacion,
                f"El enlace vence en {horas_vigencia} horas.",
            )
        )
        with self._lock:
            self.correos_enviados.append(
                CorreoSeguridadEnviado(
                    destinatario=correo,
                    asunto="Activa tu cuenta",
                    cuerpo=cuerpo,
                )
            )
        _logger.info(
            "Enlace de activación enviado a %s: %s", correo, enlace_activacion
        )

    def enviar_aviso_bloqueo_cuenta(
        self,
        usuario: Usuario,
        fecha_hora_bloqueo: datetime,
        bloqueada_hasta: datetime,
    ) -> None:
        if self.fallar_envio:
            raise RuntimeError("No fue posible enviar el correo de seguridad")

        ahora_texto = fecha_hora_bloqueo.strftime("%d/%m/%Y %H:%M")
        hora_fin = bloqueada_hasta.strftime("%H:%M")
        cuerpo = "\n".join(
            (
                f"Hola {usuario.nombres},",
                "Detectamos varios intentos fallidos de inicio de sesión en tu "
                "cuenta y la bloqueamos temporalmente por seguridad.",
                f"Bloqueo: {ahora_texto}",
                f"Podrás volver a intentarlo a las {hora_fin}.",
                "Si fuiste tú, espera a que termine el bloqueo e ingresa con tu "
                "contraseña. Si no reconoces esta actividad, comunícate con nosotros.",
            )
        )
        with self._lock:
            self.correos_enviados.append(
                CorreoSeguridadEnviado(
                    destinatario=usuario.correo,
                    asunto="Bloqueo temporal de tu cuenta",
                    cuerpo=cuerpo,
                )
            )
