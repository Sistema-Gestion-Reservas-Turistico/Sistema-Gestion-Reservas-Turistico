import hashlib
from datetime import datetime, timedelta, timezone

from app.config import MINUTOS_EXPIRACION_TOKEN, MINUTOS_INACTIVIDAD_SESION
from app.domain.exceptions.sesion import PersistenciaSesionError
from app.domain.interfaces.sesion import SesionRepository
from app.domain.models.sesion import SesionCreate, SesionRenovadaResponse
from app.services.security.jwt_tokens import crear_token_jwt


class CrearSesionUsuarioUseCase:
    def __init__(self, repositorio: SesionRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self,
        usuario_id: int,
        correo: str,
        rol: str,
        ahora: datetime | None = None,
    ) -> SesionRenovadaResponse:
        momento = ahora or datetime.now(timezone.utc)
        token = crear_token_jwt(usuario_id, rol, momento)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expira_en = momento + timedelta(minutes=MINUTOS_EXPIRACION_TOKEN)
        try:
            self._repositorio.crear(
                SesionCreate(
                    usuario_id=usuario_id,
                    correo=correo,
                    rol=rol,
                    token_hash=token_hash,
                    inicio_en=momento,
                    expira_en=expira_en,
                )
            )
        except Exception as error:
            raise PersistenciaSesionError() from error
        return SesionRenovadaResponse(
            token=token,
            tipo="Bearer",
            expira_en=MINUTOS_EXPIRACION_TOKEN * 60,
            inactividad_max=MINUTOS_INACTIVIDAD_SESION * 60,
        )
