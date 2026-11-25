import hashlib
from datetime import datetime, timezone

from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionInvalidaOCerradaError,
)
from app.domain.interfaces.sesion import SesionRepository
from app.services.use_cases.sesion_utils import cargar_sesion_vigente


class ValidarActividadSesionUseCase:
    def __init__(self, repositorio: SesionRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self, token: str, ahora: datetime | None = None
    ) -> SesionUsuario:
        momento = ahora or datetime.now(timezone.utc)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        sesion = cargar_sesion_vigente(self._repositorio, token_hash, momento)
        try:
            return self._repositorio.actualizar_actividad(token_hash, momento)
        except SesionInvalidaOCerradaError:
            raise
        except Exception as error:
            raise PersistenciaSesionError() from error