import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import (
    obtener_caso_consultar_ficha_destino,
)
from app.domain.exceptions.ficha_destino import PersistenciaFichaDestinoError
from app.main import app
from app.services.security.jwt_tokens import crear_token_jwt


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def encabezados(rol: str = "Cliente") -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token_jwt(1, rol)}"}


def test_consulta_ficha_destino_activo_sin_coordenadas(
    cliente: TestClient,
) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/destinos/15",
        headers=encabezados(),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Consulta de ficha de destino exitosa",
        "data": {
            "id_destino": 15,
            "nombre": "Reserva Natural Demo",
            "descripcion": (
                "Reserva natural con senderos ecológicos y miradores."
            ),
            "ubicacion": {
                "municipio": "Salento",
                "departamento": "Quindío",
                "pais": "Colombia",
            },
            "tipos_turismo": ["AVENTURA", "ECOTURISMO"],
            "actividades": [
                {"id": 1, "nombre": "Senderismo"},
                {"id": 2, "nombre": "Observación de aves"},
            ],
            "coordenadas": None,
            "imagen_principal_url": (
                "https://almacenamiento.ejemplo.com/destinos/15.jpg"
            ),
        },
        "success": True,
    }


def test_consulta_ficha_destino_con_coordenadas_registradas(
    cliente: TestClient,
) -> None:
    registrada = cliente.put(
        "/api/v1/geo/destinos/15/coordenadas",
        headers=encabezados("Administrador"),
        json={"latitud": 4.6372, "longitud": -75.5712},
    )
    assert registrada.status_code == 200

    respuesta = cliente.get(
        "/api/v1/geo/destinos/15",
        headers=encabezados("Cliente"),
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["coordenadas"] == {
        "latitud": 4.6372,
        "longitud": -75.5712,
    }


@pytest.mark.parametrize("id_destino", ["abc", "0", "-1"])
def test_identificador_invalido_responde_400(
    cliente: TestClient, id_destino: str
) -> None:
    respuesta = cliente.get(
        f"/api/v1/geo/destinos/{id_destino}",
        headers=encabezados(),
    )

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "El identificador del destino no es válido",
        "data": None,
        "success": False,
    }


@pytest.mark.parametrize("id_destino", ["9999", "16"])
def test_destino_inexistente_o_inactivo_responde_404(
    cliente: TestClient, id_destino: str
) -> None:
    respuesta = cliente.get(
        f"/api/v1/geo/destinos/{id_destino}",
        headers=encabezados(),
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "mensaje": "No existe un destino activo con el identificador indicado",
        "data": None,
        "success": False,
    }


def test_sin_token_o_token_invalido_responde_401(cliente: TestClient) -> None:
    ruta = "/api/v1/geo/destinos/15"

    assert cliente.get(ruta).status_code == 401
    assert cliente.get(
        ruta, headers={"Authorization": "Bearer token-invalido"}
    ).status_code == 401


def test_cualquier_rol_autenticado_puede_consultar_ficha(
    cliente: TestClient,
) -> None:
    for rol in ("Cliente", "Administrador"):
        respuesta = cliente.get(
            "/api/v1/geo/destinos/15",
            headers=encabezados(rol),
        )
        assert respuesta.status_code == 200


def test_fallo_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, id_destino):
            assert id_destino == "15"
            raise PersistenciaFichaDestinoError()

    app.dependency_overrides[obtener_caso_consultar_ficha_destino] = (
        CasoConFallo
    )
    respuesta = cliente.get(
        "/api/v1/geo/destinos/15",
        headers=encabezados(),
    )

    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible consultar la ficha del destino",
        "data": None,
        "success": False,
    }


def test_openapi_documenta_ruta_respuestas_y_ejemplos(
    cliente: TestClient,
) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"]["/api/v1/geo/destinos/{id_destino}"]["get"]
    parametro = operacion["parameters"][0]

    assert parametro["name"] == "id_destino"
    assert parametro["in"] == "path"
    assert parametro["required"] is True
    assert parametro["schema"]["type"] == "integer"
    respuestas = operacion["responses"]
    assert {"200", "400", "401", "404", "503"}.issubset(respuestas)
    for codigo in ("200", "400", "401", "404", "503"):
        assert "example" in respuestas[codigo]["content"]["application/json"]
