from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.consulta_parametros import (
    obtener_caso_consultar_parametros_categoria,
)
from app.api.schemas.valores_categorias_api import (
    ParametroVigenteData,
    ParametroVigenteResponse,
    ParametroCategoriaItemData,
    ParametrosVigentesCategoriaData,
    ParametrosVigentesCategoriaResponse,
    ValorCategoriaErrorResponse,
)
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
    ParametroNoVigenteError,
)
from app.services.use_cases.consultar_parametros_categoria import (
    ConsultarParametrosCategoria,
    ParametrosConsultaNoDisponiblesError,
)


router = APIRouter(
    prefix="/api/v1/parametros/consulta",
    tags=["Consulta pública de parámetros"],
)


@router.get(
    "/{categoria}",
    response_model=ParametrosVigentesCategoriaResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ValorCategoriaErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ValorCategoriaErrorResponse},
    },
    summary="Listar valores vigentes de una categoría",
    description=(
        "Consulta pública sin sesión. Retorna únicamente valores activos, "
        "ordenados por el campo orden."
    ),
)
def listar_parametros_vigentes(
    categoria: str,
    caso: ConsultarParametrosCategoria = Depends(
        obtener_caso_consultar_parametros_categoria
    ),
) -> ParametrosVigentesCategoriaResponse | JSONResponse:
    try:
        valores = caso.listar_vigentes(categoria)
    except CategoriaValorNoEncontradaError:
        return _error(
            status.HTTP_404_NOT_FOUND,
            "La categoría indicada no existe",
        )
    except ParametrosConsultaNoDisponiblesError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No fue posible consultar los parámetros",
        )
    return ParametrosVigentesCategoriaResponse(
        mensaje="Consulta de parámetros exitosa",
        data=ParametrosVigentesCategoriaData(
            categoria=categoria,
            valores=[
                ParametroCategoriaItemData.model_validate(valor) for valor in valores
            ],
        ),
        success=True,
    )


@router.get(
    "/{categoria}/{codigo}",
    response_model=ParametroVigenteResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ValorCategoriaErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ValorCategoriaErrorResponse},
    },
    summary="Consultar un parámetro vigente por código",
    description=(
        "Consulta pública sin sesión. La categoría y el código no distinguen "
        "mayúsculas de minúsculas."
    ),
)
def obtener_parametro_vigente(
    categoria: str,
    codigo: str,
    caso: ConsultarParametrosCategoria = Depends(
        obtener_caso_consultar_parametros_categoria
    ),
) -> ParametroVigenteResponse | JSONResponse:
    try:
        valor = caso.obtener_vigente(categoria, codigo)
    except CategoriaValorNoEncontradaError:
        return _error(
            status.HTTP_404_NOT_FOUND,
            "La categoría indicada no existe",
        )
    except ParametroNoVigenteError:
        return _error(
            status.HTTP_404_NOT_FOUND,
            "El parámetro no existe o no está vigente",
        )
    except ParametrosConsultaNoDisponiblesError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No fue posible consultar los parámetros",
        )
    return ParametroVigenteResponse(
        mensaje="Consulta de parámetro exitosa",
        data=ParametroVigenteData.model_validate(valor),
        success=True,
    )


def _error(codigo: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje, "data": None, "success": False},
    )
