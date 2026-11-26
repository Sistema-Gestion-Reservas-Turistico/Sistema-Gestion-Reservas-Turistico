import hashlib
from datetime import datetime, timezone

from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionInvalidaOCerradaError,
)
from app.domain.interfaces.sesion import SesionRepository
from app.domain.models.sesion import CerrarSesionResponse
from app.services.use_cases.sesion_utils import cargar_sesion_vigente


class CerrarSesionUseCase:
    def __init__(self, repositorio: SesionRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self, token: str, ahora: datetime | None = None
    ) -> CerrarSesionResponse:
        momento = ahora or datetime.now(timezone.utc)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        cargar_sesion_vigente(self._repositorio, token, momento)
        try:
            sesion = self._repositorio.cerrar_por_logout(token_hash, momento)
        except SesionInvalidaOCerradaError:
            raise
        except Exception as error:
            raise PersistenciaSesionError() from error
        return CerrarSesionResponse(
            mensaje="Sesión cerrada correctamente",
            motivo_cierre="LOGOUT",
            cerrada_en=sesion.cerrada_en or momento,
        )
