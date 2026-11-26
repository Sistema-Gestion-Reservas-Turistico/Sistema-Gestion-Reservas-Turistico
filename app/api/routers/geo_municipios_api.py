from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import autorizar_administrador_jwt
from app.api.dependencies.destinos import (
    obtener_caso_actualizar_disponibilidad_municipio,
)
from app.api.schemas.disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioRequest,
    DisponibilidadMunicipioDataSchema,
    DisponibilidadMunicipioResponseSchema,
    ErrorDisponibilidadMunicipioResponseSchema,
)
from app.domain.exceptions.disponibilidad_municipio import (
    DisponibilidadMunicipioInvalidaError,
    MunicipioNoEncontradoError,
    PersistenciaMunicipioError,
)
from app.domain.models.disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioCreate,
)
from app.services.use_cases.actualizar_disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioUseCase,
)


router = APIRouter(prefix="/api/v1/geo/municipios", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.patch(
    "/{id_municipio}/disponibilidad",
    response_model=DisponibilidadMunicipioResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": DisponibilidadMunicipioResponseSchema,
            "description": "Disponibilidad municipal actualizada.",
            "content": {
                "application/json": {
                    "examples": {
                        "actualizada": {
                            "value": {
                                "mensaje": (
                                    "Disponibilidad del municipio actualizada exitosamente"
                                ),
                                "data": {
                                    "id_municipio": 63130,
                                    "nombre": "Calarcá",
                                    "id_departamento": 63,
                                    "habilitado": False,
                                    "fecha_actualizacion": "2026-10-25T15:10:00-05:00",
                                },
                                "success": True,
                            }
                        },
                        "sin_cambios": {
                            "value": {
                                "mensaje": (
                                    "El municipio ya se encontraba en el estado "
                                    "solicitado (sin cambios)"
                                ),
                                "data": {
                                    "id_municipio": 63130,
                                    "nombre": "Calarcá",
                                    "id_departamento": 63,
                                    "habilitado": False,
                                    "fecha_actualizacion": "2026-10-25T15:10:00-05:00",
                                },
                                "success": True,
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDisponibilidadMunicipioResponseSchema,
            "description": "El estado debe ser booleano.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "El campo habilitado es obligatorio y debe ser verdadero o falso"
                    )
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorDisponibilidadMunicipioResponseSchema,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Authentication is required")
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorDisponibilidadMunicipioResponseSchema,
            "description": "Se requiere rol Administrador.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No tiene permisos para realizar esta acción"
                    )
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorDisponibilidadMunicipioResponseSchema,
            "description": "Municipio no encontrado.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No existe un municipio con el identificador indicado"
                    )
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorDisponibilidadMunicipioResponseSchema,
            "description": "No fue posible actualizar el municipio.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible actualizar la disponibilidad del municipio"
                    )
                }
            },
        },
    },
    summary="Actualizar disponibilidad municipal",
    description=(
        "Controla en qué municipios se muestran búsquedas y se permiten ventas."
    ),
)
def actualizar_disponibilidad_municipio(
    id_municipio: int,
    solicitud: ActualizarDisponibilidadMunicipioRequest,
    _: None = Depends(autorizar_administrador_jwt),
    caso: ActualizarDisponibilidadMunicipioUseCase = Depends(
        obtener_caso_actualizar_disponibilidad_municipio
    ),
) -> DisponibilidadMunicipioResponseSchema | JSONResponse:
    try:
        respuesta = caso.ejecutar(
            id_municipio,
            ActualizarDisponibilidadMunicipioCreate(
                habilitado=solicitud.habilitado
            ),
        )
    except DisponibilidadMunicipioInvalidaError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except MunicipioNoEncontradoError as error:
        return _error(status.HTTP_404_NOT_FOUND, str(error))
    except PersistenciaMunicipioError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return DisponibilidadMunicipioResponseSchema(
        mensaje=respuesta.mensaje,
        data=DisponibilidadMunicipioDataSchema(
            id_municipio=respuesta.data.id_municipio,
            nombre=respuesta.data.nombre,
            id_departamento=respuesta.data.id_departamento,
            habilitado=respuesta.data.habilitado,
            fecha_actualizacion=respuesta.data.fecha_actualizacion,
        ),
        success=True,
    )


def _error(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"mensaje": mensaje, "data": None, "success": False},
    )