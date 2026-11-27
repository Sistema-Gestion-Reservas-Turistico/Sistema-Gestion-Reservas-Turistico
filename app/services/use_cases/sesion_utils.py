from datetime import datetime, timedelta
import hashlib

import jwt

from app.config import MINUTOS_INACTIVIDAD_SESION
from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)
from app.domain.interfaces.sesion import SesionRepository
from app.services.security.jwt_tokens import decodificar_token_jwt


def cargar_sesion_vigente(
    repositorio: SesionRepository,
    token: str,
    ahora: datetime,
) -> SesionUsuario:
    try:
        claims = decodificar_token_jwt(token)
    except (jwt.InvalidTokenError, TypeError, ValueError) as error:
        raise SesionInvalidaOCerradaError() from error

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    try:
        sesion = repositorio.buscar_por_token_hash(token_hash)
    except Exception as error:
        raise PersistenciaSesionError() from error
    if sesion is None:
        raise SesionInvalidaOCerradaError()
    if claims["sub"] != str(sesion.usuario_id) or claims["role"] != sesion.rol:
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
