from fastapi import APIRouter, Depends, status
from app.api.responses import JSONResponse

from app.api.dependencies.parametros_pagos import (
    obtener_caso_listar_parametros_pagos,
)
from app.api.schemas.valores_categorias_api import (
    CategoriaParametroPagoData,
    ParametrosPagoData,
    ParametrosPagoErrorResponse,
    ParametrosPagoResponse,
    ValorParametroPagoData,
)
from app.domain.exceptions.parametros_pagos import (
    ParametrosPagoNoDisponiblesError,
)
from app.services.use_cases.listar_parametros_pagos import ListarParametrosPagos


router = APIRouter(
    prefix="/api/v1/parametros/pagos",
    tags=["Parámetros de pagos"],
)


@router.get(
    "",
    response_model=ParametrosPagoResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"model": ParametrosPagoErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ParametrosPagoErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ParametrosPagoErrorResponse},
    },
    summary="Listar parámetros de pagos",
)
def listar_parametros_pagos(
    caso: ListarParametrosPagos = Depends(obtener_caso_listar_parametros_pagos),
) -> ParametrosPagoResponse | JSONResponse:
    try:
        parametros = caso.ejecutar()
    except ParametrosPagoNoDisponiblesError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "mensaje": "Payment parameters could not be retrieved",
                "data": None,
                "success": False,
            },
        )
    return ParametrosPagoResponse(
        message="Payment parameters retrieved successfully",
        data=ParametrosPagoData(
            categorias=[
                CategoriaParametroPagoData(
                    clave=categoria.clave,
                    nombre=categoria.nombre,
                    valores=[
                        ValorParametroPagoData(
                            id=valor.id,
                            codigo=valor.codigo,
                            nombre=valor.nombre,
                            orden=valor.orden,
                            activo=valor.activo,
                            es_sistema=valor.es_sistema,
                        )
                        for valor in categoria.valores
                    ],
                )
                for categoria in parametros.categorias
            ]
        ),
        success=True,
    )
