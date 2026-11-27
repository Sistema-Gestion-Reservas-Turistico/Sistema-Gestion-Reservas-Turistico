import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import (
    obtener_caso_consultar_estructura_territorial,
)
from app.domain.exceptions.estructura_territorial import (
    PersistenciaEstructuraTerritorialError,
)
from app.main import app
from app.services.security.jwt_tokens import crear_token_jwt


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def encabezados(rol: str = "Administrador") -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token_jwt(1, rol)}"}


def test_consulta_filtrada_retorna_habilitados_e_inhabilitados(
    cliente: TestClient,
) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/estructura?id_pais=1&id_departamento=63",
        headers=encabezados(),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "Consulta de estructura territorial exitosa",
        "data": {
            "id_pais": 1,
            "nombre": "Colombia",
            "total_departamentos": 1,
            "total_municipios": 3,
            "departamentos": [
                {
                    "id": 63,
                    "nombre": "Quindío",
                    "municipios": [
                        {"id": 63001, "nombre": "Armenia", "habilitado": True},
                        {"id": 63130, "nombre": "Calarcá", "habilitado": False},
                        {"id": 63690, "nombre": "Salento", "habilitado": True},
                    ],
                }
            ],
        },
        "success": True,
    }


def test_pais_sin_estructura_omite_nombre_nulo(cliente: TestClient) -> None:
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/estructura?id_pais=9999",
        headers=encabezados(),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": "No existe estructura territorial para el país indicado",
        "data": {
            "id_pais": 9999,
            "total_departamentos": 0,
            "total_municipios": 0,
            "departamentos": [],
        },
        "success": False,
    }


@pytest.mark.parametrize(
    "query", ["", "?id_pais=abc", "?id_pais=0", "?id_pais=1&id_departamento=abc"]
)
def test_parametros_invalidos_responden_400(
    cliente: TestClient, query: str
) -> None:
    respuesta = cliente.get(
        f"/api/v1/geo/ubicaciones/estructura{query}",
        headers=encabezados(),
    )

    assert respuesta.status_code == 400
    esperado = (
        "El identificador del departamento debe ser numérico"
        if "id_departamento=abc" in query
        else "El identificador del país es obligatorio y debe ser numérico"
    )
    assert respuesta.json() == {
        "mensaje": esperado,
        "data": None,
        "success": False,
    }


def test_autenticacion_jwt_y_rol_administrador_son_requeridos(
    cliente: TestClient,
) -> None:
    ruta = "/api/v1/geo/ubicaciones/estructura?id_pais=1"

    assert cliente.get(ruta).status_code == 401
    assert cliente.get(
        ruta, headers={"Authorization": "Bearer token-invalido"}
    ).status_code == 401
    assert cliente.get(ruta, headers=encabezados("Cliente")).status_code == 403
    assert cliente.get(ruta, headers=encabezados()).status_code == 200


def test_fallo_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, id_pais, id_departamento=None):
            assert id_pais == "1"
            assert id_departamento is None
            raise PersistenciaEstructuraTerritorialError()

    app.dependency_overrides[
        obtener_caso_consultar_estructura_territorial
    ] = CasoConFallo
    respuesta = cliente.get(
        "/api/v1/geo/ubicaciones/estructura?id_pais=1",
        headers=encabezados(),
    )

    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible consultar la estructura territorial",
        "data": None,
        "success": False,
    }


def test_openapi_documenta_parametros_ejemplos_y_respuestas(
    cliente: TestClient,
) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"]["/api/v1/geo/ubicaciones/estructura"]["get"]
    parametros = {item["name"]: item for item in operacion["parameters"]}
    assert set(parametros) == {"id_pais", "id_departamento"}
    assert parametros["id_pais"]["required"] is False
    assert parametros["id_departamento"]["required"] is False

    respuestas = operacion["responses"]
    assert {"200", "400", "401", "403", "503"}.issubset(respuestas)
    assert "examples" in respuestas["200"]["content"]["application/json"]
    assert "examples" in respuestas["400"]["content"]["application/json"]
    for codigo in ("401", "403", "503"):
        assert "example" in respuestas[codigo]["content"]["application/json"]
