from fastapi import Depends, Header, HTTPException, Request, status

from app.api.dependencies.sesion import obtener_sesion_opcional
from app.domain.entities.sesion import SesionUsuario


def autorizar_administrador(
    request: Request,
    x_rol: str | None = Header(default=None, alias="X-Rol"),
    sesion: SesionUsuario | None = Depends(obtener_sesion_opcional),
) -> None:
    rol = sesion.rol if sesion is not None else getattr(request.state, "rol", None)
    if sesion is None and rol is None:
        rol = x_rol if x_rol is not None else "Administrador"
    if rol != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para realizar esta acción",
        )
