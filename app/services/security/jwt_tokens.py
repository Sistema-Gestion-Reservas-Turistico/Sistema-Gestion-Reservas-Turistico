from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import JWT_SECRET_KEY, MINUTOS_EXPIRACION_TOKEN


def crear_token_jwt(
    usuario_id: int,
    rol: str,
    ahora: datetime | None = None,
) -> str:
    momento = ahora or datetime.now(timezone.utc)
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    else:
        momento = momento.astimezone(timezone.utc)
    return jwt.encode(
        {
            "sub": str(usuario_id),
            "role": rol,
            "iat": momento,
            "exp": momento + timedelta(minutes=MINUTOS_EXPIRACION_TOKEN),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )


def decodificar_token_jwt(token: str) -> dict[str, Any]:
    claims = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256"],
        options={"require": ["sub", "role", "exp"]},
    )
    if not claims["sub"].isdigit() or not isinstance(claims["role"], str):
        raise jwt.InvalidTokenError("Invalid token claims")
    return claims
