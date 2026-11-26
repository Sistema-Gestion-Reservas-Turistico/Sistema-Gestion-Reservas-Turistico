from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import autorizar_administrador_jwt
from app.api.dependencies.destinos import (
    obtener_caso_registrar_coordenadas_destino,
)
from app.api.schemas.coordenadas_destino import (
    CoordenadasDestinoResponseData,
    ErrorCoordenadasResponse,
    RegistrarCoordenadasRequest,
    RegistrarCoordenadasResponse,
)
from app.domain.exceptions.destino import (
    CoincidenciaTerritorialError,
    CoordenadasFueraDeRangoError,
    DestinoNoEncontradoError,
    PersistenciaCoordenadasError,
)
from app.domain.models.destino import RegistrarCoordenadasDestinoCreate
from app.services.use_cases.registrar_coordenadas_destino import (
    RegistrarCoordenadasDestinoUseCase,
)


router = APIRouter(prefix="/api/v1/geo/destinos", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.put(
    "/{id_destino}/coordenadas",
    response_model=RegistrarCoordenadasResponse,
    responses={
        status.HTTP_200_OK: {
            "model": RegistrarCoordenadasResponse,
            "description": "Coordenadas registradas.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Coordenadas del destino registradas exitosamente",
                        "data": {
                            "id_destino": 15,
                            "nombre": "Reserva Natural Demo",
                            "id_municipio": 63690,
                            "latitud": 4.6372,
                            "longitud": -75.5712,
                            "estado_coordenadas": "REGISTRADAS",
                        },
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorCoordenadasResponse,
            "description": "Coordenadas fuera de rango.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "La latitud debe estar entre -90 y 90"
                    )
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorCoordenadasResponse,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Token JWT inválido o ausente")
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorCoordenadasResponse,
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
            "model": ErrorCoordenadasResponse,
            "description": "Destino no encontrado.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No existe un destino con el identificador indicado"
                    )
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorCoordenadasResponse,
            "description": "Coordenadas fuera del municipio.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "Las coordenadas indicadas no pertenecen al municipio asociado al destino"
                    )
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorCoordenadasResponse,
            "description": "Persistencia no disponible.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible registrar las coordenadas del destino"
                    )
                }
            },
        },
    },
    summary="Registrar coordenadas",
    description=(
        "Guarda el punto del destino usado por el mapa y la búsqueda por cercanía."
    ),
)
def registrar_coordenadas_destino(
    id_destino: int,
    solicitud: RegistrarCoordenadasRequest,
    _: None = Depends(autorizar_administrador_jwt),
    caso: RegistrarCoordenadasDestinoUseCase = Depends(
        obtener_caso_registrar_coordenadas_destino
    ),
) -> RegistrarCoordenadasResponse | JSONResponse:
    try:
        resultado = caso.ejecutar(
            id_destino,
            RegistrarCoordenadasDestinoCreate(
                latitud=solicitud.latitud,
                longitud=solicitud.longitud,
            ),
        )
    except CoordenadasFueraDeRangoError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except DestinoNoEncontradoError as error:
        return _error(status.HTTP_404_NOT_FOUND, str(error))
    except CoincidenciaTerritorialError as error:
        return _error(status.HTTP_409_CONFLICT, str(error))
    except PersistenciaCoordenadasError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return RegistrarCoordenadasResponse(
        mensaje=resultado.mensaje,
        data=CoordenadasDestinoResponseData(**vars(resultado.data)),
        success=True,
    )


def _error(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"mensaje": mensaje, "data": None, "success": False},
    )