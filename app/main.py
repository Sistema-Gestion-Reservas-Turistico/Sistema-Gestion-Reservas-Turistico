from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import Body, FastAPI
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.dependencies.parametros_transporte import (
    obtener_caso_cargar_parametros_transporte,
)
from app.api.routers.parametros_transporte_api import router as transporte_router
from app.api.routers.categorias_parametros_api import (
    router as categorias_parametros_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    obtener_caso_cargar_parametros_transporte().ejecutar()
    yield


app = FastAPI(title="Sistema de Gestión de Reservas Turístico", lifespan=lifespan)
app.include_router(categorias_parametros_router)
app.include_router(transporte_router)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, error: RequestValidationError
):
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