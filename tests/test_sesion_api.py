import hashlib
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.sesion import (
    obtener_caso_validar_actividad_sesion,
    obtener_repositorio_sesiones,
)
from app.domain.exceptions.sesion import PersistenciaSesionError
from app.domain.models.sesion import SesionCreate
from app.main import app


@pytest.fixture
def cliente():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def iniciar_sesion(cliente: TestClient) -> tuple[str, dict]:
    respuesta = cliente.post(
        "/api/v1/auth/login",
        json={
            "correo": "cliente.activo@correo.com",
            "password": "Viaje2026",
        },
    )
    assert respuesta.status_code == 200
    return respuesta.json()["data"]["token"], respuesta.json()["data"]


def test_login_emite_token_y_registra_su_hash(cliente: TestClient) -> None:
    token, data = iniciar_sesion(cliente)
    assert data["tipo"] == "Bearer"
    assert data["expira_en"] == 1800
    assert data["inactividad_max"] == 900
    sesion = obtener_repositorio_sesiones().buscar_por_token_hash(
        hashlib.sha256(token.encode("utf-8")).hexdigest()
    )
    assert sesion is not None
    assert token not in repr(sesion)


def test_me_actualiza_actividad(cliente: TestClient) -> None:
    token, _ = iniciar_sesion(cliente)
    respuesta = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200
    data = respuesta.json()["data"]
    assert data["correo"] == "cliente.activo@correo.com"
    assert data["inactividad_max"] == 900


def test_inactividad_cierra_la_sesion_con_codigo_especifico(
    cliente: TestClient,
) -> None:
    token, _ = iniciar_sesion(cliente)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    ahora = datetime.now(timezone.utc)
    obtener_repositorio_sesiones().actualizar_actividad(
        token_hash, ahora - timedelta(minutes=16)
    )
    respuesta = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    body = respuesta.json()
    assert respuesta.status_code == 401
    assert body["errorCode"] == "SESION_INACTIVA"
    assert body["data"] == {"codigo": "SESION_INACTIVA"}
    assert body["message"] == "Tu sesión se cerró por inactividad. Inicia sesión de nuevo"


def test_mantener_rota_token_y_actualiza_sesion(cliente: TestClient) -> None:
    token, _ = iniciar_sesion(cliente)
    respuesta = cliente.post(
        "/api/v1/auth/sesion/mantener",
        headers={"Authorization": f"Bearer {token}"},
    )
    token_nuevo = respuesta.json()["data"]["token"]
    assert respuesta.status_code == 200
    assert respuesta.json()["message"] == "Sesión renovada"
    assert token_nuevo != token
    anterior = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    nuevo = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token_nuevo}"}
    )
    assert anterior.status_code == 401
    assert nuevo.status_code == 200


def test_logout_invalida_el_token(cliente: TestClient) -> None:
    token, _ = iniciar_sesion(cliente)
    respuesta = cliente.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["data"]["motivo_cierre"] == "LOGOUT"
    posterior = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert posterior.status_code == 401


def test_token_expirado_responde_401(cliente: TestClient) -> None:
    ahora = datetime.now(timezone.utc)
    token = "token-expirado-de-prueba"
    obtener_repositorio_sesiones().crear(
        SesionCreate(
            usuario_id=42,
            correo="expired@correo.com",
            rol="Cliente",
            token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            inicio_en=ahora - timedelta(minutes=31),
            expira_en=ahora - timedelta(seconds=1),
        )
    )
    respuesta = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["errorCode"] == "UNAUTHORIZED"
    assert respuesta.json()["data"] is None


def test_fallo_persistencia_responde_503(cliente: TestClient) -> None:
    class CasoConFallo:
        def ejecutar(self, token: str):
            raise PersistenciaSesionError()

    app.dependency_overrides[obtener_caso_validar_actividad_sesion] = CasoConFallo
    respuesta = cliente.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer token"}
    )
    assert respuesta.status_code == 503
    assert respuesta.json()["message"] == "No fue posible validar la sesión"
    assert respuesta.json()["data"] is None


def test_openapi_documenta_rutas_y_error_de_inactividad(
    cliente: TestClient,
) -> None:
    esquema = cliente.get("/openapi.json").json()
    rutas = (
        ("/api/v1/auth/login", "post"),
        ("/api/v1/auth/me", "get"),
        ("/api/v1/auth/sesion/mantener", "post"),
        ("/api/v1/auth/logout", "post"),
    )
    login = esquema["paths"][rutas[0][0]][rutas[0][1]]
    assert login["summary"] == "Iniciar sesión"
    assert login["description"] == "Autentica al usuario y crea una sesión activa."

    def verificar_sin_ejemplos(valor: object) -> None:
        if isinstance(valor, dict):
            assert not {"example", "examples", "json_schema_extra"}.intersection(
                valor
            )
            for anidado in valor.values():
                verificar_sin_ejemplos(anidado)
        elif isinstance(valor, list):
            for anidado in valor:
                verificar_sin_ejemplos(anidado)

    for ruta, metodo in rutas:
        operacion = esquema["paths"][ruta][metodo]
        if ruta != rutas[0][0]:
            assert operacion["summary"] in {
                "Consultar sesión actual",
                "Mantener sesión",
                "Cerrar sesión",
            }
        verificar_sin_ejemplos(operacion["responses"])
        for respuesta in operacion["responses"].values():
            contenido = respuesta.get("content", {}).get("application/json", {})
            schema = contenido.get("schema", {})
            referencia = schema.get("$ref")
            if referencia is None:
                continue
            nombre_schema = referencia.rsplit("/", maxsplit=1)[-1]
            modelo = esquema["components"]["schemas"][nombre_schema]
            verificar_sin_ejemplos(modelo)
            if ruta != rutas[0][0]:
                timestamp = modelo.get("properties", {}).get("timestamp", {})
                assert "pattern" not in timestamp

    ruta_sesion, metodo_sesion = rutas[1]
    respuesta = esquema["paths"][ruta_sesion][metodo_sesion]["responses"]["401"]
    contenido = respuesta["content"]["application/json"]
    assert contenido["schema"]["$ref"].endswith("/SesionInactivaErrorResponse")
    assert "description" not in esquema["paths"][ruta_sesion][metodo_sesion]
    error_schema = esquema["components"]["schemas"]["SesionInactivaErrorResponse"]
    assert "pattern" not in error_schema["properties"]["timestamp"]


def test_admin_conserva_fallback_sin_bearer_y_rechaza_rol_cliente(
    cliente: TestClient,
) -> None:
    datos = {
        "clave": "HU10_TEST_CATEGORIA",
        "nombre": "Categoría HU10",
        "descripcion": "Prueba de fallback administrativo",
    }
    creada = cliente.post("/api/v1/parametros/categorias", json=datos)
    assert creada.status_code == 201
    rechazada_por_header = cliente.post(
        "/api/v1/parametros/categorias",
        json={**datos, "clave": "HU10_TEST_X_ROL"},
        headers={"X-Rol": "Cliente"},
    )
    assert rechazada_por_header.status_code == 403

    token, _ = iniciar_sesion(cliente)
    denegada = cliente.post(
        "/api/v1/parametros/categorias",
        json={**datos, "clave": "HU10_TEST_DENEGADA"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert denegada.status_code == 403