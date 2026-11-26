import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import (
    obtener_caso_registrar_coordenadas_destino,
    obtener_repositorio_destinos,
)
from app.domain.exceptions.destino import PersistenciaCoordenadasError
from app.main import app
from app.services.security.jwt_tokens import crear_token_jwt


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def headers(rol: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token_jwt(101, rol)}"}


def test_login_emite_jwt(cliente: TestClient) -> None:
    respuesta = cliente.post(
        "/api/v1/auth/login",
        json={"correo": "cliente.activo@correo.com", "password": "Viaje2026"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["tipo"] == "Bearer"
    assert respuesta.json()["data"]["token"]


def test_admin_registra_coordenadas_del_destino_seed(cliente: TestClient) -> None:
    respuesta = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=headers("Administrador"),
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Coordenadas del destino registradas exitosamente",
        "data": {
            "id_destino": 15,
            "nombre": "Reserva Natural Demo",
            "id_municipio": 63690,
            "latitud": 4.6372,
            "longitud": -75.5712,
            "estado_coordenadas": "REGISTRADAS",
        },
        "success": True,
    }


def test_registrar_coordenadas_sobrescribe_las_anteriores(
    cliente: TestClient,
) -> None:
    response_headers = headers("Administrador")
    for latitud, longitud in ((4.6372, -75.5712), (4.64, -75.57)):
        respuesta = cliente.put(
            "/api/v1/geo/destinos/15/coordenadas",
            headers=response_headers,
            json={"latitud": latitud, "longitud": longitud},
        )
        assert respuesta.status_code == 200
    destino = obtener_repositorio_destinos().obtener_por_id(15)
    assert destino.latitud == 4.64
    assert destino.longitud == -75.57


@pytest.mark.parametrize(
    ("payload", "mensaje"),
    [
        (
            {"latitud": 90.1, "longitud": -75.5712},
            "La latitud debe estar entre -90 y 90",
        ),
        (
            {"latitud": 4.6372, "longitud": -180.1},
            "La longitud debe estar entre -180 y 180",
        ),
        (
            {"latitud": "no-numérica", "longitud": -75.5712},
            "La latitud debe estar entre -90 y 90",
        ),
    ],
)
def test_rango_o_tipo_invalido_responde_400(cliente, payload, mensaje) -> None:
    respuesta = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=headers("Administrador"),
        json=payload,
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {"mensaje": mensaje, "data": None, "success": False}


def test_sin_token_o_token_invalido_responde_401(cliente: TestClient) -> None:
    ruta = "/api/v1/geo/destinos/15/coordenadas"
    ausente = cliente.put(ruta, json={"latitud": 4.6372, "longitud": -75.5712})
    invalido = cliente.put(
        ruta,
        headers={"Authorization": "Bearer token-invalido"},
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert ausente.status_code == 401
    assert invalido.status_code == 401


def test_usuario_sin_rol_administrador_responde_403(cliente: TestClient) -> None:
    respuesta = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=headers("Cliente"),
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert respuesta.status_code == 403


def test_destino_inexistente_responde_404(cliente: TestClient) -> None:
    respuesta = cliente.put(
        "/api/v1/geo/destinos/999/coordenadas",
        headers=headers("Administrador"),
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "mensaje": "No existe un destino con el identificador indicado",
        "data": None,
        "success": False,
    }


def test_coordenadas_fuera_del_municipio_responden_409(cliente: TestClient) -> None:
    respuesta = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=headers("Administrador"),
        json={"latitud": 4.8, "longitud": -75.5712},
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["data"] is None
    assert respuesta.json()["success"] is False


def test_fallo_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, id_destino: int, datos):
            raise PersistenciaCoordenadasError()

    app.dependency_overrides[
        obtener_caso_registrar_coordenadas_destino
    ] = CasoConFallo
    respuesta = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=headers("Administrador"),
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible registrar las coordenadas del destino",
        "data": None,
        "success": False,
    }


def test_openapi_documenta_todos_los_codigos_geo(cliente: TestClient) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"][
        "/api/v1/geo/destinos/{id_destino}/coordenadas"
    ]["put"]
    assert set(operacion["responses"]) == {
        "200",
        "400",
        "401",
        "403",
        "404",
        "409",
        "503",
    }
    for codigo in ("200", "400", "401", "403", "404", "409", "503"):
        assert "example" in operacion["responses"][codigo]["content"][
            "application/json"
        ]
    assert operacion["responses"]["400"]["content"]["application/json"][
        "example"
    ]["mensaje"] == "La latitud debe estar entre -90 y 90"
