import logging
from datetime import datetime, timedelta, timezone

from app.config import MAX_REENVIOS_ACTIVACION_POR_HORA
from app.domain.exceptions.activacion import (
    LimiteReenviosActivacionError,
    PersistenciaActivacionError,
)
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService
from app.domain.interfaces.token_activacion import TokenActivacionRepository
from app.domain.interfaces.usuarios import UsuarioRepository
from app.domain.models.activacion import (
    ReenviarActivacionRequest,
    ReenviarActivacionResponse,
)
from app.services.use_cases.activacion_utils import crear_y_enviar_token_activacion


_logger = logging.getLogger(__name__)


class ReenviarActivacionCuentaUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        tokens: TokenActivacionRepository,
        notificaciones: NotificacionCorreoService,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens
        self._notificaciones = notificaciones

    def ejecutar(
        self, solicitud: ReenviarActivacionRequest
    ) -> ReenviarActivacionResponse:
        correo = solicitud.correo.strip().lower()
        ahora = datetime.now(timezone.utc)
        try:
            permitido = self._tokens.registrar_solicitud_reenvio(
                correo_normalizado=correo,
                solicitada_en=ahora,
                maximo=MAX_REENVIOS_ACTIVACION_POR_HORA,
                ventana=timedelta(hours=1),
            )
        except Exception as error:
            raise PersistenciaActivacionError() from error
        if not permitido:
            raise LimiteReenviosActivacionError()

        try:
            usuario = self._usuarios.buscar_por_correo(correo)
        except Exception as error:
            raise PersistenciaActivacionError() from error
        if usuario is not None and usuario.estado == "PENDIENTE_ACTIVACION":
            try:
                crear_y_enviar_token_activacion(
                    usuario,
                    self._tokens,
                    self._notificaciones,
                    ahora,
                )
            except Exception as error:
                raise PersistenciaActivacionError() from error
            _logger.info("Se solicitó un nuevo enlace de activación para %s", correo)
        return ReenviarActivacionResponse(
            mensaje=(
                "Si el correo corresponde a una cuenta pendiente, enviaremos "
                "un nuevo enlace"
            )
        )
