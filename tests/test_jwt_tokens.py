import jwt
import pytest

from app.config import JWT_SECRET_KEY
from app.services.security.jwt_tokens import (
    crear_token_jwt,
    decodificar_token_jwt,
)


def test_token_jwt_contiene_identidad_rol_y_expiracion() -> None:
    token = crear_token_jwt(15, "Administrador")
    claims = decodificar_token_jwt(token)
    assert claims["sub"] == "15"
    assert claims["rol"] == "Administrador"
    assert "exp" in claims


def test_token_con_firma_invalida_se_rechaza() -> None:
    token = jwt.encode(
        {"sub": "15", "rol": "Administrador", "exp": 9999999999},
        f"{JWT_SECRET_KEY}-invalid",
        algorithm="HS256",
    )
    with pytest.raises(jwt.InvalidTokenError):
        decodificar_token_jwt(token)