from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.valores_categorias_api import (
    obtener_caso_listar_parametros_transporte,
)
from app.api.schemas.valores_categorias_api import (
    ParametrosTransporteData,
    ParametrosTransporteResponse,
    ValorCategoriaData,
    ValorCategoriaErrorResponse,
)
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
)
from app.services.use_cases.listar_parametros_transporte import (
    ListarParametrosTransporte,
)


router = APIRouter(
    prefix="/api/v1/parametros/transporte",
    tags=["Parámetros de transporte"],
)


@router.get(
    "",
    response_model=ParametrosTransporteResponse,
    responses={404: {"model": ValorCategoriaErrorResponse}},
    summary="Listar parámetros de transporte",
)
def listar_parametros_transporte(
    caso: ListarParametrosTransporte = Depends(
        obtener_caso_listar_parametros_transporte
    ),
) -> ParametrosTransporteResponse | JSONResponse:
    try:
        parametros = caso.ejecutar()
    except CategoriaValorNoEncontradaError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "mensaje": "No se encontraron las categorías de transporte iniciales",
                "data": None,
                "success": False,
            },
        )
    return ParametrosTransporteResponse(
        mensaje="Parámetros de transporte consultados correctamente",
        data=ParametrosTransporteData(
            tipo_vehiculo=[
                ValorCategoriaData.model_validate(valor)
                for valor in parametros["tipo_vehiculo"]
            ],
            estado_vehiculo=[
                ValorCategoriaData.model_validate(valor)
                for valor in parametros["estado_vehiculo"]
            ],
        ),
        success=True,
    )