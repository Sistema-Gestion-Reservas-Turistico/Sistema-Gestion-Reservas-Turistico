import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.destinos import (
    obtener_caso_actualizar_disponibilidad_municipio,
    obtener_repositorio_destinos,
    obtener_repositorio_territorios,
)
from app.domain.exceptions.disponibilidad_municipio import PersistenciaMunicipioError
from app.main import app
from app.services.security.jwt_tokens import crear_token_jwt


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def encabezados(rol: str = "Administrador") -> dict[str, str]:
    return {"Authorization": f"Bearer {crear_token_jwt(101, rol)}"}


def actualizar(cliente: TestClient, habilitado) -> object:
    return cliente.patch(
        "/api/v1/geo/municipios/63130/disponibilidad",
        headers=encabezados(),
        json={"habilitado": habilitado},
    )


def test_estado_se_refleja_en_hu11_hu13_y_preserva_destino(
    cliente: TestClient,
) -> None:
    activado = actualizar(cliente, True)
    assert activado.status_code == 200
    assert activado.json()["mensaje"] == (
        "Disponibilidad del municipio actualizada exitosamente"
    )
    assert activado.json()["data"]["habilitado"] is True
    assert activado.json()["data"]["fecha_actualizacion"].endswith("-05:00")

    municipios = cliente.get(
        "/api/v1/geo/ubicaciones?id_departamento=63",
        headers=encabezados("Cliente"),
    ).json()["data"]["ubicaciones"]
    assert "Calarcá" in [item["nombre"] for item in municipios]

    sugerencias = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=cal",
        headers=encabezados("Cliente"),
    ).json()["data"]["sugerencias"]
    assert any(
        item["nombre"] == "Calarcá" and item["departamento"] == "Quindío"
        for item in sugerencias
    )

    inhabilitado = actualizar(cliente, False)
    assert inhabilitado.status_code == 200
    assert inhabilitado.json()["data"]["habilitado"] is False
    municipios_despues = cliente.get(
        "/api/v1/geo/ubicaciones?id_departamento=63",
        headers=encabezados("Cliente"),
    ).json()["data"]["ubicaciones"]
    sugerencias_despues = cliente.get(
        "/api/v1/geo/ubicaciones/autocompletar?q=cal",
        headers=encabezados("Cliente"),
    ).json()["data"]["sugerencias"]
    assert "Calarcá" not in [item["nombre"] for item in municipios_despues]
    assert "Calarcá" not in [item["nombre"] for item in sugerencias_despues]
    assert obtener_repositorio_destinos().obtener_por_id(15) is not None


def test_mismo_estado_no_actualiza_fecha(cliente: TestClient) -> None:
    repositorio = obtener_repositorio_territorios()
    fecha = repositorio.obtener_municipio(63130).fecha_actualizacion
    respuesta = actualizar(cliente, False)
    assert respuesta.status_code == 200
    assert respuesta.json()["mensaje"] == (
        "El municipio ya se encontraba en el estado solicitado (sin cambios)"
    )
    assert repositorio.obtener_municipio(63130).fecha_actualizacion == fecha
    assert respuesta.json()["data"]["fecha_actualizacion"] == fecha.isoformat()


@pytest.mark.parametrize("body", ({}, {"habilitado": "si"}, {"habilitado": 1}, {"habilitado": 0}))
def test_body_ausente_o_no_booleano_responde_400(cliente: TestClient, body) -> None:
    respuesta = cliente.patch(
        "/api/v1/geo/municipios/63130/disponibilidad",
        headers=encabezados(),
        json=body,
    )
    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "mensaje": "El campo habilitado es obligatorio y debe ser verdadero o falso",
        "data": None,
        "success": False,
    }


def test_autenticacion_y_rol_admin_son_requeridos(cliente: TestClient) -> None:
    ruta = "/api/v1/geo/municipios/63130/disponibilidad"
    body = {"habilitado": True}
    assert cliente.patch(ruta, json=body).status_code == 401
    assert cliente.patch(
        ruta,
        headers={"Authorization": "Bearer invalid"},
        json=body,
    ).status_code == 401
    assert cliente.patch(
        ruta,
        headers=encabezados("Cliente"),
        json=body,
    ).status_code == 403


def test_municipio_inexistente_responde_404(cliente: TestClient) -> None:
    respuesta = cliente.patch(
        "/api/v1/geo/municipios/99999/disponibilidad",
        headers=encabezados(),
        json={"habilitado": True},
    )
    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "mensaje": "No existe un municipio con el identificador indicado",
        "data": None,
        "success": False,
    }


def test_error_de_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, id_municipio: int, datos):
            raise PersistenciaMunicipioError()

    app.dependency_overrides[
        obtener_caso_actualizar_disponibilidad_municipio
    ] = CasoConFallo
    respuesta = actualizar(cliente, True)
    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "mensaje": "No fue posible actualizar la disponibilidad del municipio",
        "data": None,
        "success": False,
    }


def test_openapi_documenta_respuestas_y_ejemplos(cliente: TestClient) -> None:
    openapi = cliente.get("/openapi.json").json()
    operacion = openapi["paths"][
        "/api/v1/geo/municipios/{id_municipio}/disponibilidad"
    ]["patch"]
    respuestas = operacion["responses"]
    assert {"200", "400", "401", "403", "404", "503"}.issubset(respuestas)
    assert "examples" in respuestas["200"]["content"]["application/json"]
    for codigo in ("400", "401", "403", "404", "503"):
        assert "example" in respuestas[codigo]["content"]["application/json"]
