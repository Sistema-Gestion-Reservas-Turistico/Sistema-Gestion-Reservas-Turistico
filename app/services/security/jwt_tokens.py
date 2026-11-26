from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.config import JWT_SECRET_KEY, MINUTOS_EXPIRACION_JWT


def crear_token_jwt(usuario_id: int, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(usuario_id),
            "rol": rol,
            "iat": ahora,
            "exp": ahora + timedelta(minutes=MINUTOS_EXPIRACION_JWT),
        },
        JWT_SECRET_KEY,
        algorithm="HS256",
    )


def decodificar_token_jwt(token: str) -> dict[str, Any]:
    claims = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=["HS256"],
        options={"require": ["sub", "rol", "exp"]},
    )
    if not claims["sub"].isdigit() or not isinstance(claims["rol"], str):
        raise jwt.InvalidTokenError("Invalid claims")
    return claims