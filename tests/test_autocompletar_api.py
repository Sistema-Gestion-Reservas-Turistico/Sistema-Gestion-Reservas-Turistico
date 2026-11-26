import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import obtener_caso_autocompletar_ubicaciones
from app.domain.exceptions.autocompletar_ubicaciones import (
    PersistenciaAutocompletarError,
)
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


def test_sal_retorna_salaminay_salento_con_departamento(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=sal&limite=5",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Sugerencias de ubicación encontradas",
        "data": {
            "consulta": "sal",
            "total": 2,
            "sugerencias": [
                {
                    "id": 17653,
                    "nombre": "Salamina",
                    "tipo": "MUNICIPIO",
                    "departamento": "Caldas",
                },
                {
                    "id": 63690,
                    "nombre": "Salento",
                    "tipo": "MUNICIPIO",
                    "departamento": "Quindío",
                },
            ],
        },
        "success": True,
    }


def test_busqueda_ignora_mayusculas_y_tildes(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=QUINDIO",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    sugerencias = respuesta.json()["data"]["sugerencias"]
    assert [(item["nombre"], item["departamento"]) for item in sugerencias] == [
        ("Quindío", None)
    ]


def test_solo_muestra_municipios_habilitados(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=cal",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    nombres = [
        item["nombre"] for item in respuesta.json()["data"]["sugerencias"]
    ]
    assert nombres == ["Caldas"]


def test_limite_recorta_despues_de_ordenar(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=sal&limite=1",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert data["total"] == 1
    assert data["sugerencias"][0]["nombre"] == "Salamina"


@pytest.mark.parametrize("query", ("", "q=ab", "q=%20%20", "q=ab%20"))
def test_consulta_ausente_o_corta_responde_400(
    cliente: TestClient, query: str
) -> None:
    suffix = f"?{query}" if query else ""
    respuesta = cliente.get(
        f"/api/v1/geo/ubicaciones/autocompletar{suffix}",
        headers=encabezados(),
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "El texto de búsqueda debe tener al menos 3 caracteres",
        "data": None,
        "success": False,
    }


@pytest.mark.parametrize("limite", ("abc", "0", "-3", "1.5"))
def test_limite_invalido_responde_400(cliente: TestClient, limite: str) -> None:
    respuesta = cliente.get(
        f"/api/v1/geo/ubicaciones/autocompletar?q=sal&limite={limite}",
        headers=encabezados(),
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "El límite debe ser un entero positivo",
        "data": None,
        "success": False,
    }


def test_sin_coincidencias_responde_200_false(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=xyz",
        headers=encabezados(),
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "No se encontraron ubicaciones que coincidan con el texto ingresado",
        "data": {"consulta": "xyz", "total": 0, "sugerencias": []},
        "success": False,
    }


def test_requiere_jwt_valido_y_acepta_cualquier_rol(cliente: TestClient) -> None:
    ruta = "/api/v1/geo/ubicaciones/autocompletar?q=sal"
    assert cliente.get(ruta).status_code == 401
    assert (
        cliente.get(ruta, headers={"Authorization": "Bearer invalid"}).status_code
        == 401
    )
    assert cliente.get(ruta, headers=encabezados("Cliente")).status_code == 200


def test_error_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, q: str, limite: int):
            raise PersistenciaAutocompletarError()

    app.dependency_overrides[
        obtener_caso_autocompletar_ubicaciones
    ] = CasoConFallo
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=sal",
        headers=encabezados(),
    )
    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible consultar las sugerencias de ubicación",
        "data": None,
        "success": False,
    }


def test_openapi_documenta_parametros_y_ejemplos(cliente: TestClient) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"][
        "/api/v1/geo/ubicaciones/autocompletar"
    ]["get"]
    parametros = {item["name"]: item for item in operacion["parameters"]}
    assert set(parametros) == {"q", "limite"}
    assert parametros["q"]["required"] is False
    assert parametros["limite"]["required"] is False
    respuestas = operacion["responses"]
    assert {"200", "400", "401", "503"}.issubset(respuestas)
    assert "examples" in respuestas["200"]["content"]["application/json"]
    assert "example" in respuestas["400"]["content"]["application/json"]
    assert "example" in respuestas["401"]["content"]["application/json"]
    assert "example" in respuestas["503"]["content"]["application/json"]
