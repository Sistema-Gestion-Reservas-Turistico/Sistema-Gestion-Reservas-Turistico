import hashlib
from datetime import datetime, timedelta, timezone

from app.config import MINUTOS_EXPIRACION_TOKEN, MINUTOS_INACTIVIDAD_SESION
from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionInvalidaOCerradaError,
)
from app.domain.interfaces.sesion import SesionRepository
from app.domain.models.sesion import SesionRenovadaResponse
from app.services.use_cases.sesion_utils import cargar_sesion_vigente
from app.services.security.jwt_tokens import crear_token_jwt


class MantenerSesionUseCase:
    def __init__(self, repositorio: SesionRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self, token: str, ahora: datetime | None = None
    ) -> SesionRenovadaResponse:
        momento = ahora or datetime.now(timezone.utc)
        token_hash_actual = hashlib.sha256(token.encode("utf-8")).hexdigest()
        sesion = cargar_sesion_vigente(self._repositorio, token, momento)
        token_nuevo = crear_token_jwt(sesion.usuario_id, sesion.rol, momento)
        token_hash_nuevo = hashlib.sha256(token_nuevo.encode("utf-8")).hexdigest()
        expira_en = momento + timedelta(minutes=MINUTOS_EXPIRACION_TOKEN)
        try:
            self._repositorio.renovar_token(
                token_hash_actual,
                token_hash_nuevo,
                momento,
                expira_en,
            )
        except SesionInvalidaOCerradaError:
            raise
        except Exception as error:
            raise PersistenciaSesionError() from error
        return SesionRenovadaResponse(
            token=token_nuevo,
            tipo="Bearer",
            expira_en=MINUTOS_EXPIRACION_TOKEN * 60,
            inactividad_max=MINUTOS_INACTIVIDAD_SESION * 60,
        )
