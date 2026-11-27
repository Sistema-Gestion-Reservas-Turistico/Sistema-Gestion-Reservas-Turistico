from fastapi import APIRouter, Depends, status
from app.api.responses import JSONResponse

from app.api.dependencies.categorias_parametros import (
    obtener_caso_actualizar_categoria_parametro,
    obtener_caso_crear_categoria_parametro,
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.autorizacion import autorizar_administrador
from app.api.dependencies.valores_categorias_api import (
    obtener_caso_actualizar_estado_valor_categoria,
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
    CambiarEstadoValorCategoria,
    ValorCategoriaCrear,
    ValorCategoriaData,
    ValorCategoriaEditar,
    ValorCategoriaErrorResponse,
    ValorCategoriaEstadoData,
    ValorCategoriaEstadoResponse,
    ValorCategoriaResponse,
    ValoresCategoriaResponse,
)
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
    CategoriaParametroNoEncontradaError,
)
from app.domain.exceptions.parametros_pagos import UltimoMetodoPagoActivoError
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
    ValorCategoriaDuplicadoError,
    ValorCategoriaNoEncontradoError,
    ValorCategoriaSistemaNoInactivableError,
    ValorCategoriaSistemaSoloEditableError,
)
from app.services.use_cases.actualizar_categoria_parametro import (
    ActualizarCategoriaParametro,
)
from app.services.use_cases.crear_categoria_parametro import CrearCategoriaParametro
from app.services.use_cases.actualizar_valor_categoria_parametro import (
    ActualizarValorCategoriaParametro,
)
from app.services.use_cases.actualizar_estado_valor_categoria_parametro import (
    ActualizarEstadoValorCategoriaParametro,
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
        message="Categories retrieved successfully",
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
        403: {"model": CategoriaParametroErrorResponse},
    },
)
def crear_categoria_parametro(
    datos: CategoriaParametroCrear,
    caso: CrearCategoriaParametro = Depends(obtener_caso_crear_categoria_parametro),
    _: None = Depends(autorizar_administrador),
) -> CategoriaParametroResponse | JSONResponse:
    try:
        categoria = caso.ejecutar(**datos.model_dump())
    except CategoriaParametroDuplicadaError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "A category with the specified key already exists",
                "data": None,
                "success": False,
            },
        )
    return CategoriaParametroResponse(
        message="Category saved successfully",
        data=categoria,
        success=True,
    )


@router.put(
    "/{id}",
    response_model=CategoriaParametroResponse,
    responses={
        400: {"model": CategoriaParametroErrorResponse},
        404: {"model": CategoriaParametroErrorResponse},
        403: {"model": CategoriaParametroErrorResponse},
    },
)
def actualizar_categoria_parametro(
    id: int,
    datos: CategoriaParametroEditar,
    caso: ActualizarCategoriaParametro = Depends(
        obtener_caso_actualizar_categoria_parametro
    ),
    _: None = Depends(autorizar_administrador),
) -> CategoriaParametroResponse | JSONResponse:
    if datos.nombre is None and datos.descripcion is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "mensaje": "Provide a name or description to update the category",
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
                "mensaje": "The specified category was not found",
                "data": None,
                "success": False,
            },
        )
    return CategoriaParametroResponse(
        message="Category updated successfully",
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
    activo: bool | None = None,
    caso: ListarValoresCategoriaParametro = Depends(
        obtener_caso_listar_valores_categoria
    ),
) -> ValoresCategoriaResponse | JSONResponse:
    try:
        valores = caso.ejecutar(clave, activo)
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "The specified category does not exist",
                "data": None,
                "success": False,
            },
        )
    return ValoresCategoriaResponse(
        message="Category values retrieved successfully",
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
        403: {"model": ValorCategoriaErrorResponse},
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
    _: None = Depends(autorizar_administrador),
) -> ValorCategoriaResponse | JSONResponse:
    try:
        valor = caso.ejecutar(clave, **datos.model_dump())
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "The specified category does not exist",
                "data": None,
                "success": False,
            },
        )
    except ValorCategoriaDuplicadoError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "A value with the specified code already exists in this category",
                "data": None,
                "success": False,
            },
        )
    return ValorCategoriaResponse(
        message="Category value created successfully",
        data=ValorCategoriaData.model_validate(valor),
        success=True,
    )


@router.put(
    "/{clave}/valores/{id}",
    response_model=ValorCategoriaResponse,
    responses={
        400: {"model": ValorCategoriaErrorResponse},
        404: {"model": ValorCategoriaErrorResponse},
        403: {"model": ValorCategoriaErrorResponse},
        409: {"model": ValorCategoriaErrorResponse},
    },
    summary="Editar un valor de categoría",
    description=(
        "Edita nombre, descripción u orden; el código no se puede modificar. "
        "Los valores de sistema solo permiten editar nombre y descripción."
    ),
)
def actualizar_valor_categoria(
    clave: str,
    id: int,
    datos: ValorCategoriaEditar,
    caso: ActualizarValorCategoriaParametro = Depends(
        obtener_caso_actualizar_valor_categoria
    ),
    _: None = Depends(autorizar_administrador),
) -> ValorCategoriaResponse | JSONResponse:
    if not datos.model_fields_set:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "mensaje": "Provide a name, description, or order to update the value",
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
                "mensaje": "The specified category does not exist",
                "data": None,
                "success": False,
            },
        )
    except ValorCategoriaNoEncontradoError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "The specified value does not exist in this category",
                "data": None,
                "success": False,
            },
        )
    except ValorCategoriaSistemaSoloEditableError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": (
                    "System-required values allow only their name and description "
                    "to be updated"
                ),
                "data": None,
                "success": False,
            },
        )
    return ValorCategoriaResponse(
        message="Category value updated successfully",
        data=ValorCategoriaData.model_validate(valor),
        success=True,
    )


@router.patch(
    "/{clave}/valores/{id}/estado",
    response_model=ValorCategoriaEstadoResponse,
    responses={
        400: {"model": ValorCategoriaErrorResponse},
        404: {"model": ValorCategoriaErrorResponse},
        409: {"model": ValorCategoriaErrorResponse},
        403: {"model": ValorCategoriaErrorResponse},
    },
    summary="Activar o inactivar un valor",
    description=(
        "Cambia el estado del valor sin eliminarlo. El listado administrativo "
        "incluye todos los estados y permite filtrarlos mediante el parámetro activo."
    ),
)
def actualizar_estado_valor_categoria(
    clave: str,
    id: int,
    datos: CambiarEstadoValorCategoria,
    caso: ActualizarEstadoValorCategoriaParametro = Depends(
        obtener_caso_actualizar_estado_valor_categoria
    ),
    _: None = Depends(autorizar_administrador),
) -> ValorCategoriaEstadoResponse | JSONResponse:
    try:
        valor = caso.ejecutar(clave, id, datos.activo)
    except ValorCategoriaSistemaNoInactivableError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": (
                    "This value is required by the system and cannot be deactivated"
                ),
                "data": None,
                "success": False,
            },
        )
    except UltimoMetodoPagoActivoError:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "mensaje": "At least one payment method must remain active",
                "data": None,
                "success": False,
                "errorCode": "LAST_ACTIVE_PAYMENT_METHOD",
            },
        )
    except ValorCategoriaNoEncontradoError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "The specified value was not found",
                "data": None,
                "success": False,
            },
        )
    return ValorCategoriaEstadoResponse(
        message="Category value status updated successfully",
        data=ValorCategoriaEstadoData(
            id=valor.id,
            categoria=valor.categoria,
            codigo=valor.codigo,
            activo=valor.activo,
        ),
        success=True,
    )
