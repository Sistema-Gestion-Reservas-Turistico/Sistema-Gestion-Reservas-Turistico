from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Body, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.openapi.utils import get_openapi
from app.api.responses import (
    ApiErrorResponse,
    ApiResponse,
    JSONResponse,
    api_error_response,
    english_error_message,
    error_code_for_message,
    utc_timestamp,
)

from app.api.dependencies.parametros_transporte import (
    obtener_caso_cargar_parametros_transporte,
)
from app.api.routers.parametros_transporte_api import router as transporte_router
from app.api.routers.categorias_parametros_api import (
    router as categorias_parametros_router,
)
from app.api.dependencies.parametros_pagos import (
    obtener_caso_cargar_parametros_pagos,
)
from app.api.routers.parametros_pagos_api import router as pagos_router
from app.api.routers.consulta_parametros_api import router as consulta_parametros_router
from app.api.dependencies.parametros_alojamiento_alimentacion import (
    obtener_caso_cargar_parametros_alojamiento_alimentacion,
)
from app.api.routers.parametros_alojamiento_alimentacion_api import (
    router as alojamiento_alimentacion_router,
)
from app.api.dependencies.usuarios import obtener_caso_cargar_parametros_usuarios
from app.api.routers.usuarios_api import router as usuarios_router
from app.api.routers.auth_api import router as auth_router
from app.domain.exceptions.sesion import (
    PersistenciaSesionError,
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    obtener_caso_cargar_parametros_transporte().ejecutar()
    obtener_caso_cargar_parametros_pagos().ejecutar()
    obtener_caso_cargar_parametros_alojamiento_alimentacion().ejecutar()
    obtener_caso_cargar_parametros_usuarios().ejecutar()
    yield


app = FastAPI(title="Sistema de Gestión de Reservas Turístico", lifespan=lifespan)
app.include_router(categorias_parametros_router)
app.include_router(transporte_router)
app.include_router(pagos_router)
app.include_router(consulta_parametros_router)
app.include_router(alojamiento_alimentacion_router)
app.include_router(usuarios_router)
app.include_router(auth_router)

_RUTAS_AUTH = {
    "/api/v1/auth/login",
    "/api/v1/auth/me",
    "/api/v1/auth/sesion/mantener",
    "/api/v1/auth/logout",
}


def generar_openapi():
    if app.openapi_schema is not None:
        return app.openapi_schema
    esquema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    ejemplos_error = (
        esquema["paths"]["/api/v1/parametros/alojamiento-alimentacion"]["get"][
            "responses"
        ]
    )
    for codigo in ("403", "503"):
        ejemplos = ejemplos_error[codigo]["content"]["application/json"]["examples"]
        for ejemplo in ejemplos.values():
            ejemplo["value"]["data"] = None

    esquema["components"]["schemas"]["ApiResponse"] = ApiResponse[object].model_json_schema()
    esquema["components"]["schemas"]["ApiErrorResponse"] = (
        ApiErrorResponse.model_json_schema()
    )
    validation_response = {
        "description": "Request validation failed",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/ApiErrorResponse"},
                "example": {
                    "success": False,
                    "message": "Request validation failed",
                    "timestamp": utc_timestamp(),
                    "errorCode": "VALIDATION_ERROR",
                    "data": None,
                },
            }
        },
    }
    for ruta, path_item in esquema["paths"].items():
        for operation in path_item.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue
            if ruta in _RUTAS_AUTH:
                respuesta_validacion = {
                    "description": "Request validation failed",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SesionErrorResponse"
                            }
                        }
                    },
                }
                respuesta_interna = {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/SesionErrorResponse"
                            }
                        }
                    },
                }
            else:
                respuesta_validacion = validation_response
                respuesta_interna = {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ApiErrorResponse"},
                            "example": {
                                "success": False,
                                "message": "An unexpected server error occurred",
                                "timestamp": utc_timestamp(),
                                "errorCode": "INTERNAL_SERVER_ERROR",
                                "data": None,
                            },
                        }
                    },
                }
            operation["responses"]["422"] = respuesta_validacion.copy()
            if ruta == "/api/v1/auth/login":
                operation["responses"].pop("422", None)
                operation["responses"]["400"] = {
                    **respuesta_validacion,
                    "description": "Email or password field is missing or invalid",
                }
            operation["responses"].setdefault("500", respuesta_interna)
            for codigo, response in operation["responses"].items():
                status_code = int(codigo) if str(codigo).isdigit() else 500
                for media_type in response.get("content", {}).values():
                    if ruta in _RUTAS_AUTH:
                        media_type.pop("example", None)
                        media_type.pop("examples", None)
                    if isinstance(media_type.get("example"), dict):
                        media_type["example"] = _envolver_ejemplo(
                            media_type["example"], status_code
                        )
                    for ejemplo in media_type.get("examples", {}).values():
                        if isinstance(ejemplo.get("value"), dict):
                            ejemplo["value"] = _envolver_ejemplo(
                                ejemplo["value"], status_code
                            )
    esquema["paths"]["/api/v1/auth/login"]["post"]["responses"]["200"][
        "content"
    ]["application/json"]["example"] = {
        "success": True,
        "message": "Login successful",
        "timestamp": utc_timestamp(),
        "errorCode": None,
        "data": {
            "token": "<signed-jwt>",
            "token_type": "Bearer",
            "expires_in": 1800,
            "inactivity_timeout": 900,
            "user": {
                "id": 101,
                "first_name": "Laura",
                "last_name": "Gomez",
                "role": "Cliente",
            },
        },
    }
    app.openapi_schema = esquema
    return esquema


def _envolver_ejemplo(ejemplo: dict, status_code: int) -> dict:
    success = bool(ejemplo.get("success", status_code < 400))
    message = ejemplo.get("message", ejemplo.get("mensaje"))
    if not isinstance(message, str):
        message = "Request completed successfully" if success else "The request failed"
    message = english_error_message(message, status_code)
    error_code = (
        None
        if success
        else ejemplo.get("errorCode")
        or error_code_for_message(message, status_code)
    )
    return {
        "success": success,
        "message": message,
        "timestamp": utc_timestamp(),
        "errorCode": error_code,
        "data": (
            ejemplo.get("data")
            if success or error_code == "SESION_INACTIVA"
            else None
        ),
    }


app.openapi = generar_openapi


@app.exception_handler(HTTPException)
async def manejar_error_http(request: Request, error: HTTPException):
    messages = {
        400: "The request is invalid",
        401: "Authentication is required",
        403: "Administrator access is required",
        404: "The requested resource was not found",
        409: "The request conflicts with the current resource state",
        410: "The requested resource has expired",
        422: "Request validation failed",
        423: "The account is temporarily locked",
        429: "Too many requests. Try again later",
        503: "The service is temporarily unavailable",
    }
    message = messages.get(error.status_code, "The request failed")
    return api_error_response(error.status_code, message)


@app.exception_handler(SesionCerradaPorInactividadError)
async def manejar_sesion_inactiva(
    _: Request, error: SesionCerradaPorInactividadError
):
    return api_error_response(
        401,
        str(error),
        error.codigo,
        {"code": error.codigo},
    )


@app.exception_handler(SesionInvalidaOCerradaError)
async def manejar_sesion_invalida(_: Request, error: SesionInvalidaOCerradaError):
    return api_error_response(401, str(error), "UNAUTHORIZED")


@app.exception_handler(PersistenciaSesionError)
async def manejar_persistencia_sesion(_: Request, error: PersistenciaSesionError):
    return api_error_response(503, str(error), "SERVICE_UNAVAILABLE")


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, error: RequestValidationError
):
    if request.url.path == "/api/v1/auth/login":
        errores = error.errors()
        campos = {str(item.get("loc", ("",))[-1]) for item in errores}
        if "email" in campos or "correo" in campos:
            mensaje = "The email field is required"
        elif "password" in campos:
            mensaje = "The password field is required"
        else:
            mensaje = "The login data is invalid"
        return api_error_response(400, mensaje, "VALIDATION_ERROR")

    if request.url.path == "/api/v1/usuarios/registro":
        return api_error_response(400, "Registration data is invalid", "VALIDATION_ERROR")

    if not request.url.path.startswith("/api/v1/parametros/categorias"):
        return api_error_response(422, "Request validation failed", "VALIDATION_ERROR")

    errores = error.errors()
    if "/valores" in request.url.path:
        if request.method == "PATCH":
            mensaje = "The active field must be a boolean"
        elif request.method == "PUT" and any(
            "codigo" in item.get("loc", ())
            and item.get("type") == "extra_forbidden"
            for item in errores
        ):
            mensaje = "A value code cannot be changed"
        elif any(
            "codigo" in item.get("loc", ()) and item.get("type") == "missing"
            for item in errores
        ):
            mensaje = "The code field is required"
        elif any(
            "nombre" in item.get("loc", ()) and item.get("type") == "missing"
            for item in errores
        ):
            mensaje = "The name field is required"
        elif any("nombre" in item.get("loc", ()) for item in errores):
            mensaje = "The name is required and must not exceed 100 characters"
        elif any("orden" in item.get("loc", ()) for item in errores):
            mensaje = "The order must be an integer"
        else:
            mensaje = "The value data is invalid"
        return api_error_response(400, mensaje, "VALIDATION_ERROR")

    if request.method == "PUT" and any(
        "clave" in item.get("loc", ()) and item.get("type") == "extra_forbidden"
        for item in errores
    ):
        mensaje = "A category key cannot be changed"
    elif any(
        "clave" in item.get("loc", ()) and item.get("type") == "missing"
        for item in errores
    ):
        mensaje = "The key field is required"
    elif any(
        "clave" in item.get("loc", ()) and item.get("type") == "string_too_long"
        for item in errores
    ):
        mensaje = "The key must not exceed 50 characters"
    elif any("clave" in item.get("loc", ()) for item in errores):
        mensaje = "The key can contain only uppercase letters, numbers, and underscores"
    elif any("nombre" in item.get("loc", ()) for item in errores):
        mensaje = "The name is required and must not exceed 100 characters"
    else:
        mensaje = "The key and name fields are required"
    return api_error_response(400, mensaje, "VALIDATION_ERROR")


@app.exception_handler(Exception)
async def manejar_error_interno(_: Request, error: Exception):
    return api_error_response(
        500,
        "An unexpected server error occurred",
        "INTERNAL_SERVER_ERROR",
    )


@app.get("/")
def read_root() -> ApiResponse[None]:
    return ApiResponse[None](
        success=True,
        message="API is running successfully",
        data=None,
    )


@app.get("/prueba")
def consulta_prueba() -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        message="Test completed successfully",
        data={"prueba": "esto es prueba"},
    )

@app.post("/prueba")
def inserta_prueba(id: str = Body(..., embed=True)) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        message="Test completed successfully",
        data={"prueba": "esto es prueba", "id": id},
    )

@app.put("/prueba/{id}")
def actualizar_prueba(
    id: str, id2: str = Body(..., embed=True)
) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        message="Test updated successfully",
        data={"prueba": "estoy actualizando la prueba", "id_original": id, "nuevo_id": id2},
    )

@app.delete("/prueba/{id}")
def eliminar_prueba(id: str) -> ApiResponse[dict[str, str]]:
    return ApiResponse[dict[str, str]](
        success=True,
        message="Test deleted successfully",
        data={"prueba": "eliminando la prueba", "id_eliminado": id},
    )
