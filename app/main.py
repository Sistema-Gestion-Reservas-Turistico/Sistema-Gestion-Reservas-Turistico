from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Body, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse as FastAPIJSONResponse
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
from app.api.dependencies.destinos import (
    obtener_caso_cargar_destinos_geograficos,
)
from app.api.routers.usuarios_api import router as usuarios_router
from app.api.routers.auth_api import router as auth_router
from app.api.routers.geo_destinos_api import router as geo_router
from app.api.routers.geo_ubicaciones_api import router as geo_ubicaciones_router
from app.api.routers.geo_autocompletar_api import router as geo_autocompletar_router
from app.api.routers.geo_municipios_api import router as geo_municipios_router
from app.api.routers.geo_estructura_territorial_api import (
    router as geo_estructura_territorial_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    obtener_caso_cargar_parametros_transporte().ejecutar()
    obtener_caso_cargar_parametros_pagos().ejecutar()
    obtener_caso_cargar_parametros_alojamiento_alimentacion().ejecutar()
    obtener_caso_cargar_parametros_usuarios().ejecutar()
    obtener_caso_cargar_destinos_geograficos().ejecutar()
    yield


app = FastAPI(title="Sistema de Gestión de Reservas Turístico", lifespan=lifespan)
app.include_router(categorias_parametros_router)
app.include_router(transporte_router)
app.include_router(pagos_router)
app.include_router(consulta_parametros_router)
app.include_router(alojamiento_alimentacion_router)
app.include_router(usuarios_router)
app.include_router(auth_router)
app.include_router(geo_router)
app.include_router(geo_ubicaciones_router)
app.include_router(geo_autocompletar_router)
app.include_router(geo_municipios_router)
app.include_router(geo_estructura_territorial_router)


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
            if ruta in {
                "/api/v1/geo/destinos/{id_destino}/coordenadas",
                "/api/v1/geo/ubicaciones",
                "/api/v1/geo/ubicaciones/autocompletar",
                "/api/v1/geo/municipios/{id_municipio}/disponibilidad",
            }:
                operation["responses"].pop("422", None)
                continue
            operation["responses"]["422"] = validation_response.copy()
            operation["responses"].setdefault(
                "500",
                {
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
                },
            )
            for codigo, response in operation["responses"].items():
                status_code = int(codigo) if str(codigo).isdigit() else 500
                for media_type in response.get("content", {}).values():
                    if isinstance(media_type.get("example"), dict):
                        media_type["example"] = _envolver_ejemplo(
                            media_type["example"], status_code
                        )
                    for ejemplo in media_type.get("examples", {}).values():
                        if isinstance(ejemplo.get("value"), dict):
                            ejemplo["value"] = _envolver_ejemplo(
                                ejemplo["value"], status_code
                            )
    app.openapi_schema = esquema
    return esquema


def _envolver_ejemplo(ejemplo: dict, status_code: int) -> dict:
    success = bool(ejemplo.get("success", status_code < 400))
    message = ejemplo.get("message", ejemplo.get("mensaje"))
    if not isinstance(message, str):
        message = "Request completed successfully" if success else "The request failed"
    message = english_error_message(message, status_code)
    return {
        "success": success,
        "message": message,
        "timestamp": utc_timestamp(),
        "errorCode": (
            None
            if success
            else ejemplo.get("errorCode")
            or error_code_for_message(message, status_code)
        ),
        "data": ejemplo.get("data") if success else None,
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


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, error: RequestValidationError
):
    if request.url.path.startswith("/api/v1/geo/municipios/"):
        return FastAPIJSONResponse(
            status_code=400,
            content={
                "mensaje": (
                    "El campo habilitado es obligatorio y debe ser verdadero o falso"
                ),
                "data": None,
                "success": False,
            },
        )

    if request.url.path.startswith("/api/v1/geo/destinos/"):
        errores = error.errors()
        campo = next(
            (
                str(item.get("loc", ())[-1])
                for item in errores
                if item.get("loc") and item.get("loc", ())[-1] in {"latitud", "longitud"}
            ),
            "latitud",
        )
        mensaje = (
            "La latitud debe estar entre -90 y 90"
            if campo == "latitud"
            else "La longitud debe estar entre -180 y 180"
        )
        return FastAPIJSONResponse(
            status_code=400,
            content={"mensaje": mensaje, "data": None, "success": False},
        )

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
