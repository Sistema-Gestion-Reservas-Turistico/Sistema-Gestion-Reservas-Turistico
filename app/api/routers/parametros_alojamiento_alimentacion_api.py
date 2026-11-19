from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.parametros_alojamiento_alimentacion import (
    obtener_caso_listar_parametros_alojamiento_alimentacion,
)
from app.api.dependencies.autorizacion import autorizar_administrador
from app.api.schemas.valores_categorias_api import (
    CategoriaAlojamientoAlimentacionData,
    ParametrosAlojamientoAlimentacionData,
    ParametrosAlojamientoAlimentacionErrorResponse,
    ParametrosAlojamientoAlimentacionResponse,
    ValorAlojamientoAlimentacionData,
)
from app.domain.exceptions.parametros_alojamiento_alimentacion import (
    ParametrosAlojamientoAlimentacionNoDisponiblesError,
)
from app.services.use_cases.listar_parametros_alojamiento_alimentacion import (
    ListarParametrosAlojamientoAlimentacion,
)


router = APIRouter(
    prefix="/api/v1/parametros/alojamiento-alimentacion",
    tags=["Parámetros de alojamiento y alimentación"],
)

_ERROR_PERMISOS = {
    "summary": "Sin permisos",
    "value": {
        "mensaje": "No tiene permisos para realizar esta acción",
        "data": None,
        "success": False,
    },
}
_ERROR_CONSULTA = {
    "summary": "Servicio no disponible",
    "value": {
        "mensaje": (
            "No fue posible consultar los parámetros de alojamiento y alimentación"
        ),
        "data": None,
        "success": False,
    },
}


@router.get(
    "",
    response_model=ParametrosAlojamientoAlimentacionResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Consulta exitosa",
            "content": {
                "application/json": {
                    "examples": {
                        "consulta_exitosa": {
                            "summary": "Parámetros agrupados",
                            "value": {
                                "mensaje": (
                                    "Consulta de parámetros de alojamiento y "
                                    "alimentación exitosa"
                                ),
                                "data": {
                                    "categorias": [
                                        {
                                            "clave": "TIPO_HABITACION",
                                            "nombre": "Tipo de habitación",
                                            "valores": [
                                                {
                                                    "id": 31,
                                                    "codigo": "SENCILLA",
                                                    "nombre": "Sencilla",
                                                    "orden": 1,
                                                    "activo": True,
                                                    "es_sistema": False,
                                                }
                                            ],
                                        },
                                        {
                                            "clave": "TIPO_ALIMENTACION",
                                            "nombre": "Tipo de alimentación",
                                            "valores": [
                                                {
                                                    "id": 41,
                                                    "codigo": "DESAYUNO",
                                                    "nombre": "Solo desayuno",
                                                    "orden": 1,
                                                    "activo": True,
                                                    "es_sistema": False,
                                                }
                                            ],
                                        },
                                        {
                                            "clave": "RESTRICCION_ALIMENTARIA",
                                            "nombre": "Restricción alimentaria",
                                            "valores": [
                                                {
                                                    "id": 51,
                                                    "codigo": "VEGETARIANA",
                                                    "nombre": "Vegetariana",
                                                    "orden": 1,
                                                    "activo": True,
                                                    "es_sistema": False,
                                                }
                                            ],
                                        },
                                    ]
                                },
                                "success": True,
                            },
                        }
                    }
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ParametrosAlojamientoAlimentacionErrorResponse,
            "description": "No autorizado",
            "content": {
                "application/json": {
                    "examples": {"sin_permisos": _ERROR_PERMISOS}
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ParametrosAlojamientoAlimentacionErrorResponse,
            "description": "No fue posible consultar los parámetros",
            "content": {
                "application/json": {
                    "examples": {"error_consulta": _ERROR_CONSULTA}
                }
            },
        },
    },
    summary="Listar parámetros de alojamiento y alimentación",
)
def listar_parametros_alojamiento_alimentacion(
    caso: ListarParametrosAlojamientoAlimentacion = Depends(
        obtener_caso_listar_parametros_alojamiento_alimentacion
    ),
    _: None = Depends(autorizar_administrador),
) -> ParametrosAlojamientoAlimentacionResponse | JSONResponse:
    try:
        parametros = caso.ejecutar()
    except ParametrosAlojamientoAlimentacionNoDisponiblesError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_ERROR_CONSULTA["value"],
        )
    return ParametrosAlojamientoAlimentacionResponse(
        mensaje="Consulta de parámetros de alojamiento y alimentación exitosa",
        data=ParametrosAlojamientoAlimentacionData(
            categorias=[
                CategoriaAlojamientoAlimentacionData(
                    clave=categoria.clave,
                    nombre=categoria.nombre,
                    valores=[
                        ValorAlojamientoAlimentacionData(
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
