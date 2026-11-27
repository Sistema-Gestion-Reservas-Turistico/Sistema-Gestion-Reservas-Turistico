from functools import lru_cache

from fastapi import Depends, Header, HTTPException, Request, status

from app.domain.entities.sesion import SesionUsuario
from app.repositories.adapters.in_memory_sesion_repository import (
    InMemorySesionRepository,
)
from app.services.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.services.use_cases.crear_sesion_usuario import CrearSesionUsuarioUseCase
from app.services.use_cases.mantener_sesion import MantenerSesionUseCase
from app.services.use_cases.validar_actividad_sesion import (
    ValidarActividadSesionUseCase,
)


@lru_cache
def obtener_repositorio_sesiones() -> InMemorySesionRepository:
    return InMemorySesionRepository()


def obtener_caso_crear_sesion() -> CrearSesionUsuarioUseCase:
    return CrearSesionUsuarioUseCase(obtener_repositorio_sesiones())


def obtener_caso_validar_actividad_sesion() -> ValidarActividadSesionUseCase:
    return ValidarActividadSesionUseCase(obtener_repositorio_sesiones())


def obtener_caso_mantener_sesion() -> MantenerSesionUseCase:
    return MantenerSesionUseCase(obtener_repositorio_sesiones())


def obtener_caso_cerrar_sesion() -> CerrarSesionUseCase:
    return CerrarSesionUseCase(obtener_repositorio_sesiones())


def obtener_token_bearer(
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> str:
    return _extraer_token(authorization)


def obtener_sesion_activa(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    caso: ValidarActividadSesionUseCase = Depends(
        obtener_caso_validar_actividad_sesion
    ),
) -> SesionUsuario:
    return _validar_y_adjuntar_rol(request, authorization, caso)


def obtener_sesion_opcional(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    caso: ValidarActividadSesionUseCase = Depends(
        obtener_caso_validar_actividad_sesion
    ),
) -> SesionUsuario | None:
    if authorization is None:
        return None
    return _validar_y_adjuntar_rol(request, authorization, caso)


def _validar_y_adjuntar_rol(
    request: Request,
    authorization: str | None,
    caso: ValidarActividadSesionUseCase,
) -> SesionUsuario:
    token = _extraer_token(authorization)
    sesion = caso.ejecutar(token)
    request.state.rol = sesion.rol
    return sesion


def _extraer_token(authorization: str | None) -> str:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
        )
    esquema, separador, token = authorization.partition(" ")
    if (
        not separador
        or esquema.casefold() != "bearer"
        or not token.strip()
        or " " in token.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
        )
    return token.strip()