from fastapi import Header, HTTPException, Request, status


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
            detail="Solo el rol Administrador puede realizar operaciones de escritura",
        )
