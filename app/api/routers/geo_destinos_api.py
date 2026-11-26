from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import (
    autenticar_jwt,
    autorizar_administrador_jwt,
)
from app.api.dependencies.destinos import (
    obtener_caso_consultar_ficha_destino,
    obtener_caso_registrar_coordenadas_destino,
)
from app.api.schemas.coordenadas_destino import (
    CoordenadasDestinoResponseData,
    ErrorCoordenadasResponse,
    RegistrarCoordenadasRequest,
    RegistrarCoordenadasResponse,
)
from app.api.schemas.ficha_destino import (
    ActividadDestinoItemSchema,
    CoordenadasDestinoItemSchema,
    ErrorFichaDestinoResponseSchema,
    FichaDestinoDataSchema,
    FichaDestinoResponseSchema,
    UbicacionDestinoDataSchema,
)
from app.domain.exceptions.destino import (
    CoincidenciaTerritorialError,
    CoordenadasFueraDeRangoError,
    DestinoNoEncontradoError,
    PersistenciaCoordenadasError,
)
from app.domain.exceptions.ficha_destino import (
    DestinoActivoNoEncontradoError,
    IdentificadorDestinoInvalidoError,
    PersistenciaFichaDestinoError,
)
from app.domain.models.destino import RegistrarCoordenadasDestinoCreate
from app.services.use_cases.consultar_ficha_destino import (
    ConsultarFichaDestinoUseCase,
)
from app.services.use_cases.registrar_coordenadas_destino import (
    RegistrarCoordenadasDestinoUseCase,
)


router = APIRouter(prefix="/api/v1/geo/destinos", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.get(
    "/{id_destino}",
    response_model=FichaDestinoResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": FichaDestinoResponseSchema,
            "description": "Ficha del destino activo.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Consulta de ficha de destino exitosa",
                        "data": {
                            "id_destino": 15,
                            "nombre": "Reserva Natural Demo",
                            "descripcion": (
                                "Reserva natural con senderos ecológicos y miradores."
                            ),
                            "ubicacion": {
                                "municipio": "Salento",
                                "departamento": "Quindío",
                                "pais": "Colombia",
                            },
                            "tipos_turismo": ["AVENTURA", "ECOTURISMO"],
                            "actividades": [
                                {"id": 1, "nombre": "Senderismo"},
                                {
                                    "id": 2,
                                    "nombre": "Observación de aves",
                                },
                            ],
                            "coordenadas": {
                                "latitud": 4.6372,
                                "longitud": -75.5712,
                            },
                            "imagen_principal_url": (
                                "https://almacenamiento.ejemplo.com/destinos/15.jpg"
                            ),
                        },
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorFichaDestinoResponseSchema,
            "description": "El identificador debe ser un entero positivo.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "El identificador del destino no es válido"
                    )
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorFichaDestinoResponseSchema,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Authentication is required")
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorFichaDestinoResponseSchema,
            "description": "El destino no existe o está inactivo.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No existe un destino activo con el identificador indicado"
                    )
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorFichaDestinoResponseSchema,
            "description": "No fue posible consultar la ficha.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible consultar la ficha del destino"
                    )
                }
            },
        },
    },
    summary="Consultar ficha de destino",
    description=(
        "Devuelve la ficha de un destino activo con su ubicación territorial, "
        "tipos de turismo, actividades, coordenadas registradas e imagen. "
        "Requiere un JWT válido; se acepta cualquier rol autenticado."
    ),
)
def consultar_ficha_destino(
    id_destino: str = Path(
        ...,
        description="Identificador entero positivo del destino.",
        json_schema_extra={"type": "integer"},
    ),
    _: dict = Depends(autenticar_jwt),
    caso: ConsultarFichaDestinoUseCase = Depends(
        obtener_caso_consultar_ficha_destino
    ),
) -> FichaDestinoResponseSchema | JSONResponse:
    try:
        respuesta = caso.ejecutar(id_destino)
    except IdentificadorDestinoInvalidoError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except DestinoActivoNoEncontradoError as error:
        return _error(status.HTTP_404_NOT_FOUND, str(error))
    except PersistenciaFichaDestinoError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return FichaDestinoResponseSchema(
        mensaje=respuesta.mensaje,
        data=FichaDestinoDataSchema(
            id_destino=respuesta.data.id_destino,
            nombre=respuesta.data.nombre,
            descripcion=respuesta.data.descripcion,
            ubicacion=UbicacionDestinoDataSchema(
                municipio=respuesta.data.ubicacion.municipio,
                departamento=respuesta.data.ubicacion.departamento,
                pais=respuesta.data.ubicacion.pais,
            ),
            tipos_turismo=respuesta.data.tipos_turismo,
            actividades=[
                ActividadDestinoItemSchema(id=item.id, nombre=item.nombre)
                for item in respuesta.data.actividades
            ],
            coordenadas=(
                CoordenadasDestinoItemSchema(
                    latitud=respuesta.data.coordenadas.latitud,
                    longitud=respuesta.data.coordenadas.longitud,
                )
                if respuesta.data.coordenadas is not None
                else None
            ),
            imagen_principal_url=respuesta.data.imagen_principal_url,
        ),
        success=respuesta.success,
    )


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