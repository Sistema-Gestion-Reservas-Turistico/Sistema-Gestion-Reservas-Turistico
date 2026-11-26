from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import autenticar_jwt
from app.api.dependencies.destinos import (
    obtener_caso_consultar_ubicaciones_dinamicas,
)
from app.api.schemas.ubicaciones import (
    ConsultaUbicacionesDataSchema,
    ConsultaUbicacionesResponseSchema,
    ErrorUbicacionesResponseSchema,
    UbicacionItemSchema,
)
from app.domain.exceptions.ubicaciones import (
    ParametrosUbicacionInvalidosError,
    PersistenciaUbicacionesError,
)
from app.services.use_cases.consultar_ubicaciones_dinamicas import (
    ConsultarUbicacionesDinamicasUseCase,
)


router = APIRouter(prefix="/api/v1/geo/ubicaciones", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.get(
    "",
    response_model=ConsultaUbicacionesResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": ConsultaUbicacionesResponseSchema,
            "description": "Ubicaciones del siguiente nivel territorial.",
            "content": {
                "application/json": {
                    "examples": {
                        "departamentos": {
                            "value": {
                                "mensaje": "Consulta de ubicaciones exitosa",
                                "data": {
                                    "nivel": "DEPARTAMENTO",
                                    "id_padre": 1,
                                    "total": 3,
                                    "ubicaciones": [
                                        {"id": 5, "nombre": "Antioquia"},
                                        {"id": 63, "nombre": "Quindío"},
                                        {"id": 68, "nombre": "Santander"},
                                    ],
                                },
                                "success": True,
                            }
                        },
                        "sin_resultados": {
                            "value": {
                                "mensaje": (
                                    "No existen ubicaciones para el identificador indicado"
                                ),
                                "data": {
                                    "nivel": "MUNICIPIO",
                                    "id_padre": 9999,
                                    "total": 0,
                                    "ubicaciones": [],
                                },
                                "success": False,
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorUbicacionesResponseSchema,
            "description": "Parámetros de consulta inválidos.",
            "content": {
                "application/json": {
                    "examples": {
                        "identificador": {
                            "value": _ejemplo_error(
                                "El identificador de ubicación debe ser numérico"
                            )
                        },
                        "parametros_simultaneos": {
                            "value": _ejemplo_error(
                                "No se permite enviar id_pais e id_departamento en la misma solicitud"
                            )
                        },
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorUbicacionesResponseSchema,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Authentication is required")
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorUbicacionesResponseSchema,
            "description": "Consulta no disponible.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible consultar las ubicaciones"
                    )
                }
            },
        },
    },
    summary="Consultar ubicaciones",
    description="Permite elegir país, departamento y municipio de forma encadenada.",
)
def consultar_ubicaciones(
    id_pais: str | None = Query(
        default=None, description="Filtra departamentos por país."
    ),
    id_departamento: str | None = Query(
        default=None, description="Filtra municipios por departamento."
    ),
    _: dict = Depends(autenticar_jwt),
    caso: ConsultarUbicacionesDinamicasUseCase = Depends(
        obtener_caso_consultar_ubicaciones_dinamicas
    ),
) -> ConsultaUbicacionesResponseSchema | JSONResponse:
    try:
        if id_pais is not None and id_departamento is not None:
            raise ParametrosUbicacionInvalidosError(
                "No se permite enviar id_pais e id_departamento en la misma solicitud"
            )
        pais = _convertir_identificador(id_pais)
        departamento = _convertir_identificador(id_departamento)
        respuesta = caso.ejecutar(pais, departamento)
    except ParametrosUbicacionInvalidosError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except PersistenciaUbicacionesError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return ConsultaUbicacionesResponseSchema(
        mensaje=respuesta.mensaje,
        data=ConsultaUbicacionesDataSchema(
            nivel=respuesta.data.nivel,
            id_padre=respuesta.data.id_padre,
            total=respuesta.data.total,
            ubicaciones=[
                UbicacionItemSchema(id=item.id, nombre=item.nombre)
                for item in respuesta.data.ubicaciones
            ],
        ),
        success=respuesta.success,
    )


def _convertir_identificador(valor: str | None) -> int | None:
    if valor is None:
        return None
    try:
        return int(valor)
    except ValueError as error:
        raise ParametrosUbicacionInvalidosError(
            "El identificador de ubicación debe ser numérico"
        ) from error


def _error(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"mensaje": mensaje, "data": None, "success": False},
    )