import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import (
    obtener_caso_consultar_ubicaciones_dinamicas,
)
from app.domain.exceptions.ubicaciones import PersistenciaUbicacionesError
from app.main import app
from app.services.security.jwt_tokens import crear_token_jwt


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def encabezados(rol: str = "Cliente") -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token_jwt(101, rol)}"}


def test_sin_parametros_lista_paises(cliente: TestClient) -> None:
    respuesta = cliente.get("/api/v1/geo/ubicaciones", headers=encabezados())
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Consulta de ubicaciones exitosa",
        "data": {
            "nivel": "PAIS",
            "id_padre": None,
            "total": 1,
            "ubicaciones": [{"id": 1, "nombre": "Colombia"}],
        },
        "success": True,
    }


def test_id_pais_lista_departamentos_ordenados(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones?id_pais=1", headers=encabezados()
    )
    assert respuesta.status_code == 200
    assert [
        item["nombre"] for item in respuesta.json()["data"]["ubicaciones"]
    ] == ["Antioquia", "Quindío", "Santander"]


def test_id_departamento_lista_municipios_habilitados(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones?id_departamento=63",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    assert [
        item["nombre"] for item in respuesta.json()["data"]["ubicaciones"]
    ] == ["Armenia", "Salento"]


def test_padre_sin_registros_responde_200_y_success_false(
    cliente: TestClient,
) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones?id_departamento=9999",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "No existen ubicaciones para el identificador indicado",
        "data": {
            "nivel": "MUNICIPIO",
            "id_padre": 9999,
            "total": 0,
            "ubicaciones": [],
        },
        "success": False,
    }


@pytest.mark.parametrize(
    "query",
    (
        "id_pais=abc",
        "id_departamento=xyz",
        "id_pais=0",
        "id_departamento=-5",
    ),
)
def test_identificador_invalido_responde_400(cliente: TestClient, query: str) -> None:
    respuesta = cliente.get(
        f"/api/v1/geo/ubicaciones?{query}", headers=encabezados()
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "El identificador de ubicación debe ser numérico",
        "data": None,
        "success": False,
    }


def test_parametros_simultaneos_responden_400(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones?id_pais=1&id_departamento=63",
        headers=encabezados(),
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": (
            "No se permite enviar id_pais e id_departamento en la misma solicitud"
        ),
        "data": None,
        "success": False,
    }


def test_jwt_es_requerido_y_se_acepta_cualquier_rol(cliente: TestClient) -> None:
    ruta = "/api/v1/geo/ubicaciones"
    assert cliente.get(ruta).status_code == 401
    assert cliente.get(ruta, headers={"Authorization": "Bearer invalid"}).status_code == 401
    assert cliente.get(ruta, headers=encabezados("Cliente")).status_code == 200


def test_fallo_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, id_pais=None, id_departamento=None):
            raise PersistenciaUbicacionesError()

    app.dependency_overrides[
        obtener_caso_consultar_ubicaciones_dinamicas
    ] = CasoConFallo
    respuesta = cliente.get("/api/v1/geo/ubicaciones", headers=encabezados())
    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible consultar las ubicaciones",
        "data": None,
        "success": False,
    }


def test_openapi_incluye_ejemplos_de_exito_y_error(cliente: TestClient) -> None:
    esquema = cliente.get("/openapi.json").json()
    operacion = esquema["paths"]["/api/v1/geo/ubicaciones"]["get"]
    parametros = {item["name"]: item for item in operacion["parameters"]}
    assert set(parametros) == {"id_pais", "id_departamento"}
    assert parametros["id_pais"]["required"] is False
    assert parametros["id_departamento"]["required"] is False
    respuestas = operacion["responses"]
    assert {"200", "400", "401", "503"}.issubset(respuestas)
    assert "examples" in respuestas["200"]["content"]["application/json"]
    assert "examples" in respuestas["400"]["content"]["application/json"]
    assert "example" in respuestas["401"]["content"]["application/json"]
    assert "example" in respuestas["503"]["content"]["application/json"]
