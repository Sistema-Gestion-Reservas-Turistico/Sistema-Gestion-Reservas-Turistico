from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.usuario import Usuario
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService


@dataclass(frozen=True)
class CorreoSeguridadEnviado:
    destinatario: str
    asunto: str
    cuerpo: str


class InMemoryNotificacionCorreoService(NotificacionCorreoService):
    def __init__(self) -> None:
        self.correos_enviados: list[CorreoSeguridadEnviado] = []
        self.fallar_envio = False

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
        self.correos_enviados.append(
            CorreoSeguridadEnviado(
                destinatario=usuario.correo,
                asunto="Bloqueo temporal de tu cuenta",
                cuerpo=cuerpo,
            )
        )
