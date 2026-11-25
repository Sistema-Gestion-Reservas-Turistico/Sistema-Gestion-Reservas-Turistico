from datetime import datetime, timedelta

from app.config import MINUTOS_INACTIVIDAD_SESION
from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)
from app.domain.interfaces.sesion import SesionRepository


def cargar_sesion_vigente(
    repositorio: SesionRepository,
    token_hash: str,
    ahora: datetime,
) -> SesionUsuario:
    try:
        sesion = repositorio.buscar_por_token_hash(token_hash)
    except Exception as error:
        raise PersistenciaSesionError() from error
    if sesion is None:
        raise SesionInvalidaOCerradaError()

    try:
        sesion.validar_para_uso(
            ahora,
            timedelta(minutes=MINUTOS_INACTIVIDAD_SESION),
        )
    except SesionCerradaPorInactividadError:
        if sesion.activa:
            try:
                repositorio.cerrar_por_inactividad(token_hash, ahora)
            except Exception as error:
                raise PersistenciaSesionError() from error
        raise
    return sesion