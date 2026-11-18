from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Body, FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

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
    esquema["paths"]["/api/v1/usuarios/registro"]["post"]["responses"].pop(
        "422", None
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
    app.openapi_schema = esquema
    return esquema


app.openapi = generar_openapi


@app.exception_handler(HTTPException)
async def manejar_error_http(request: Request, error: HTTPException):
    if error.status_code == 403:
        return JSONResponse(
            status_code=403,
            content={
                "mensaje": str(error.detail),
                "data": None,
                "success": False,
            },
        )
    return await http_exception_handler(request, error)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, error: RequestValidationError
):
    if request.url.path == "/api/v1/usuarios/registro":
        errores = []
        for item in error.errors():
            ubicacion = item.get("loc", ())
            campo = next(
                (
                    parte
                    for parte in reversed(ubicacion)
                    if isinstance(parte, str) and parte not in {"body", "query"}
                ),
                "body",
            )
            detalle = str(item.get("msg", "Dato inválido"))
            if detalle.startswith("Value error, "):
                detalle = detalle.removeprefix("Value error, ")
            errores.append({"campo": campo, "detalle": detalle})
        return JSONResponse(
            status_code=400,
            content={
                "mensaje": "Los datos de registro no son válidos",
                "data": {"errores": errores},
                "success": False,
            },
        )

    if not request.url.path.startswith("/api/v1/parametros/categorias"):
        return await request_validation_exception_handler(request, error)

    errores = error.errors()
    if "/valores" in request.url.path:
        if request.method == "PATCH":
            mensaje = "El campo activo debe ser verdadero o falso"
        elif request.method == "PUT" and any(
            "codigo" in item.get("loc", ())
            and item.get("type") == "extra_forbidden"
            for item in errores
        ):
            mensaje = "El código de un valor no se puede modificar"
        elif any(
            "codigo" in item.get("loc", ()) and item.get("type") == "missing"
            for item in errores
        ):
            mensaje = "El código es obligatorio"
        elif any(
            "nombre" in item.get("loc", ()) and item.get("type") == "missing"
            for item in errores
        ):
            mensaje = "El nombre es obligatorio"
        elif any("nombre" in item.get("loc", ()) for item in errores):
            mensaje = "El nombre es obligatorio y debe tener máximo 100 caracteres"
        elif any("orden" in item.get("loc", ()) for item in errores):
            mensaje = "El orden debe ser un entero"
        else:
            mensaje = "Los datos del valor son inválidos"
        return JSONResponse(
            status_code=400,
            content={"mensaje": mensaje, "data": None, "success": False},
        )

    if request.method == "PUT" and any(
        "clave" in item.get("loc", ()) and item.get("type") == "extra_forbidden"
        for item in errores
    ):
        mensaje = "La clave de una categoría no se puede modificar"
    elif any(
        "clave" in item.get("loc", ()) and item.get("type") == "missing"
        for item in errores
    ):
        mensaje = "La clave es obligatoria"
    elif any(
        "clave" in item.get("loc", ()) and item.get("type") == "string_too_long"
        for item in errores
    ):
        mensaje = "La clave debe tener máximo 50 caracteres"
    elif any("clave" in item.get("loc", ()) for item in errores):
        mensaje = "La clave solo admite mayúsculas, números y guion bajo"
    elif any("nombre" in item.get("loc", ()) for item in errores):
        mensaje = "El nombre es obligatorio y debe tener máximo 100 caracteres"
    else:
        mensaje = "La clave y el nombre son obligatorios"
    return JSONResponse(
        status_code=400,
        content={"mensaje": mensaje, "data": None, "success": False},
    )


@app.get("/")
def read_root():
    return {"message": "API corriendo correctamente"}


@app.get("/prueba")
def consulta_prueba():
    return {"prueba": "esto es prueba"}

@app.post("/prueba")
def inserta_prueba(id: str = Body(..., embed=True)):
    return {"prueba": "esto es prueba", "id": id}

@app.put("/prueba/{id}")
def actualizar_prueba(id: str, id2: str = Body(..., embed=True)):
    return {
        "prueba": "estoy actualizando la prueba",
        "id_original": id,
        "nuevo_id": id2
    }

@app.delete("/prueba/{id}")
def eliminar_prueba(id: str):
    return {
        "prueba": "eliminando la prueba",
        "id_eliminado": id
    }
