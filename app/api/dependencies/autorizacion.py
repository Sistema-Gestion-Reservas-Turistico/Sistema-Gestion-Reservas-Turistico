import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.security.jwt_tokens import decodificar_token_jwt


def autorizar_administrador(
    request: Request,
    x_rol: str | None = Header(default=None, alias="X-Rol"),
) -> None:
    rol = getattr(request.state, "rol", None)
    if rol is None:
        rol = x_rol if x_rol is not None else "Administrador"
    if rol != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción",
        )


_bearer = HTTPBearer(auto_error=False)


def autorizar_administrador_jwt(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    if credenciales is None or credenciales.scheme.casefold() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
        )
    try:
        claims = decodificar_token_jwt(credenciales.credentials)
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required",
        ) from error

    rol = claims["rol"]
    request.state.rol = rol
    if rol != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción",
        )
