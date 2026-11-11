from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.categorias_parametros import (
    obtener_caso_actualizar_categoria_parametro,
    obtener_caso_crear_categoria_parametro,
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_caso_actualizar_valor_categoria,
    obtener_caso_crear_valor_categoria,
    obtener_caso_listar_valores_categoria,
)
from app.api.schemas.categorias_parametros import (
    CategoriaParametroCrear,
    CategoriaParametroEditar,
    CategoriaParametroErrorResponse,
    CategoriaParametroResponse,
    CategoriasParametroResponse,
)
from app.api.schemas.valores_categorias_api import (
    ValorCategoriaCrear,
    ValorCategoriaData,
    ValorCategoriaEditar,
    ValorCategoriaErrorResponse,
    ValorCategoriaResponse,
    ValoresCategoriaResponse,
)
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
    CategoriaParametroNoEncontradaError,
)
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
    ValorCategoriaDuplicadoError,
    ValorCategoriaNoEncontradoError,
)
from app.services.use_cases.actualizar_categoria_parametro import (
    ActualizarCategoriaParametro,
)
from app.services.use_cases.crear_categoria_parametro import CrearCategoriaParametro
from app.services.use_cases.actualizar_valor_categoria_parametro import (
    ActualizarValorCategoriaParametro,
)
from app.services.use_cases.crear_valor_categoria_parametro import (
    CrearValorCategoriaParametro,
)
from app.services.use_cases.listar_valores_categoria_parametro import (
    ListarValoresCategoriaParametro,
)


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


@router.get(
    "/{clave}/valores",
    response_model=ValoresCategoriaResponse,
    responses={404: {"model": ValorCategoriaErrorResponse}},
    summary="Listar valores de una categoría",
    description="Retorna los valores de la categoría ordenados por el campo orden.",
)
def listar_valores_categoria(
    clave: str,
    caso: ListarValoresCategoriaParametro = Depends(
        obtener_caso_listar_valores_categoria
    ),
) -> ValoresCategoriaResponse | JSONResponse:
    try:
        valores = caso.ejecutar(clave)
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "La categoría indicada no existe",
                "data": None,
                "success": False,
            },
        )
    return ValoresCategoriaResponse(
        mensaje="Valores consultados correctamente",
        data=[ValorCategoriaData.model_validate(valor) for valor in valores],
        success=True,
    )


@router.post(
    "/{clave}/valores",
    response_model=ValorCategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ValorCategoriaErrorResponse},
        404: {"model": ValorCategoriaErrorResponse},
        409: {"model": ValorCategoriaErrorResponse},
    },
    summary="Crear un valor de categoría",
    description=(
        "Crea un valor activo. Si no se indica orden, se agrega al final de la lista."
    ),
)
def crear_valor_categoria(
    clave: str,
    datos: ValorCategoriaCrear,
    caso: CrearValorCategoriaParametro = Depends(
        obtener_caso_crear_valor_categoria
    ),
) -> ValorCategoriaResponse | JSONResponse:
    try:
        valor = caso.ejecutar(clave, **datos.model_dump())
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "La categoría indicada no existe",
                "data": None,
                "success": False,
            },
        )
    except ValorCategoriaDuplicadoError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "Ya existe un valor con el código indicado en esta categoría",
                "data": None,
                "success": False,
            },
        )
    return ValorCategoriaResponse(
        mensaje="Valor guardado correctamente",
        data=ValorCategoriaData.model_validate(valor),
        success=True,
    )


@router.put(
    "/{clave}/valores/{id}",
    response_model=ValorCategoriaResponse,
    responses={
        400: {"model": ValorCategoriaErrorResponse},
        404: {"model": ValorCategoriaErrorResponse},
    },
    summary="Editar un valor de categoría",
    description="Edita nombre, descripción u orden; el código no se puede modificar.",
)
def actualizar_valor_categoria(
    clave: str,
    id: int,
    datos: ValorCategoriaEditar,
    caso: ActualizarValorCategoriaParametro = Depends(
        obtener_caso_actualizar_valor_categoria
    ),
) -> ValorCategoriaResponse | JSONResponse:
    if not datos.model_fields_set:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "mensaje": "Debe indicar nombre, descripción u orden para actualizar",
                "data": None,
                "success": False,
            },
        )
    try:
        valor = caso.ejecutar(
            clave,
            id,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            orden=datos.orden,
        )
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "La categoría indicada no existe",
                "data": None,
                "success": False,
            },
        )
    except ValorCategoriaNoEncontradoError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "El valor indicado no existe en esta categoría",
                "data": None,
                "success": False,
            },
        )
    return ValorCategoriaResponse(
        mensaje="Valor guardado correctamente",
        data=ValorCategoriaData.model_validate(valor),
        success=True,
    )

