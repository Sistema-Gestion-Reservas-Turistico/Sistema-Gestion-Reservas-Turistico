import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from app.config import FRONTEND_URL, HORAS_VIGENCIA_TOKEN_ACTIVACION
from app.domain.entities.token_activacion import TokenActivacionCuenta
from app.domain.entities.usuario import Usuario
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService
from app.domain.interfaces.token_activacion import TokenActivacionRepository


_logger = logging.getLogger(__name__)


def crear_y_enviar_token_activacion(
    usuario: Usuario,
    tokens: TokenActivacionRepository,
    notificaciones: NotificacionCorreoService,
    ahora: datetime | None = None,
) -> TokenActivacionCuenta:
    momento = ahora or datetime.now(timezone.utc)
    token_plano = secrets.token_hex(16)
    token_hash = hashlib.sha256(token_plano.encode("utf-8")).hexdigest()
    token = TokenActivacionCuenta(
        id=0,
        usuario_id=usuario.id,
        correo_normalizado=usuario.correo.strip().lower(),
        token_hash=token_hash,
        creado_en=momento,
        expira_en=momento + timedelta(hours=HORAS_VIGENCIA_TOKEN_ACTIVACION),
    )
    token_guardado = tokens.guardar(token)
    enlace = f"{FRONTEND_URL}/activar-cuenta?{urlencode({'token': token_plano})}"
    try:
        notificaciones.enviar_enlace_activacion(
            correo=usuario.correo,
            nombres=usuario.nombres,
            enlace_activacion=enlace,
            horas_vigencia=HORAS_VIGENCIA_TOKEN_ACTIVACION,
        )
    except Exception:
        _logger.exception(
            "No fue posible enviar el enlace de activación a %s", usuario.correo
        )
    return token_guardado
