from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.categorias_parametros import (
    obtener_caso_actualizar_categoria_parametro,
    obtener_caso_crear_categoria_parametro,
    obtener_repositorio_categoria_parametro,
)
from app.api.schemas.categorias_parametros import (
    CategoriaParametroCrear,
    CategoriaParametroEditar,
    CategoriaParametroErrorResponse,
    CategoriaParametroResponse,
    CategoriasParametroResponse,
)
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
    CategoriaParametroNoEncontradaError,
)
from app.services.use_cases.actualizar_categoria_parametro import (
    ActualizarCategoriaParametro,
)
from app.services.use_cases.crear_categoria_parametro import CrearCategoriaParametro


router = APIRouter(
    prefix="/api/v1/parametros/categorias",
    tags=["Categorías de parámetros"],
)


@router.get("", response_model=CategoriasParametroResponse)
def listar_categorias_parametros() -> CategoriasParametroResponse:
    categorias = obtener_repositorio_categoria_parametro().listar()
    return CategoriasParametroResponse(
        mensaje="Categorías consultadas correctamente",
        data=categorias,
        success=True,
    )


@router.post(
    "",
    response_model=CategoriaParametroResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": CategoriaParametroErrorResponse},
        409: {"model": CategoriaParametroErrorResponse},
    },
)
def crear_categoria_parametro(
    datos: CategoriaParametroCrear,
    caso: CrearCategoriaParametro = Depends(obtener_caso_crear_categoria_parametro),
) -> CategoriaParametroResponse | JSONResponse:
    try:
        categoria = caso.ejecutar(**datos.model_dump())
    except CategoriaParametroDuplicadaError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "Ya existe una categoría con la clave indicada",
                "data": None,
                "success": False,
            },
        )
    return CategoriaParametroResponse(
        mensaje="Categoría guardada correctamente",
        data=categoria,
        success=True,
    )


@router.put(
    "/{id}",
    response_model=CategoriaParametroResponse,
    responses={
        400: {"model": CategoriaParametroErrorResponse},
        404: {"model": CategoriaParametroErrorResponse},
    },
)
def actualizar_categoria_parametro(
    id: int,
    datos: CategoriaParametroEditar,
    caso: ActualizarCategoriaParametro = Depends(
        obtener_caso_actualizar_categoria_parametro
    ),
) -> CategoriaParametroResponse | JSONResponse:
    if datos.nombre is None and datos.descripcion is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "mensaje": "Debe indicar el nombre o la descripción para actualizar",
                "data": None,
                "success": False,
            },
        )
    try:
        categoria = caso.ejecutar(
            id,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
        )
    except CategoriaParametroNoEncontradaError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "No se encontró la categoría indicada",
                "data": None,
                "success": False,
            },
        )
    return CategoriaParametroResponse(
        mensaje="Categoría guardada correctamente",
        data=categoria,
        success=True,
    )
