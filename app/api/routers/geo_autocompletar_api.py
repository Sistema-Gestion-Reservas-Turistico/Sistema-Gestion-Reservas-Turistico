from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import autenticar_jwt
from app.api.dependencies.destinos import obtener_caso_autocompletar_ubicaciones
from app.api.schemas.autocompletar_ubicaciones import (
    AutocompletarUbicacionesDataSchema,
    AutocompletarUbicacionesResponseSchema,
    ErrorAutocompletarResponseSchema,
    SugerenciaUbicacionItemSchema,
)
from app.domain.exceptions.autocompletar_ubicaciones import (
    ConsultaAutocompletarInvalidaError,
    PersistenciaAutocompletarError,
)
from app.services.use_cases.autocompletar_ubicaciones import (
    AutocompletarUbicacionesUseCase,
)


router = APIRouter(prefix="/api/v1/geo/ubicaciones", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.get(
    "/autocompletar",
    response_model=AutocompletarUbicacionesResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": AutocompletarUbicacionesResponseSchema,
            "description": "Sugerencias de ubicación encontradas.",
            "content": {
                "application/json": {
                    "examples": {
                        "coincidencias": {
                            "value": {
                                "mensaje": "Sugerencias de ubicación encontradas",
                                "data": {
                                    "consulta": "sal",
                                    "total": 2,
                                    "sugerencias": [
                                        {
                                            "id": 17653,
                                            "nombre": "Salamina",
                                            "tipo": "MUNICIPIO",
                                            "departamento": "Caldas",
                                        },
                                        {
                                            "id": 63690,
                                            "nombre": "Salento",
                                            "tipo": "MUNICIPIO",
                                            "departamento": "Quindío",
                                        },
                                    ],
                                },
                                "success": True,
                            }
                        },
                        "sin_coincidencias": {
                            "value": {
                                "mensaje": (
                                    "No se encontraron ubicaciones que coincidan "
                                    "con el texto ingresado"
                                ),
                                "data": {
                                    "consulta": "xyz",
                                    "total": 0,
                                    "sugerencias": [],
                                },
                                "success": False,
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorAutocompletarResponseSchema,
            "description": "Texto o límite inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "El texto de búsqueda debe tener al menos 3 caracteres"
                    )
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorAutocompletarResponseSchema,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Authentication is required")
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorAutocompletarResponseSchema,
            "description": "Consulta no disponible.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible consultar las sugerencias de ubicación"
                    )
                }
            },
        },
    },
    summary="Autocompletar ubicación",
    description="Busca departamentos y municipios habilitados por nombre.",
)
def autocompletar_ubicaciones(
    q: str | None = Query(default=None, description="Texto de búsqueda."),
    limite: str = Query(default="10", description="Máximo de sugerencias."),
    _: dict = Depends(autenticar_jwt),
    caso: AutocompletarUbicacionesUseCase = Depends(
        obtener_caso_autocompletar_ubicaciones
    ),
) -> AutocompletarUbicacionesResponseSchema | JSONResponse:
    try:
        limite_numerico = int(limite)
    except ValueError:
        return _error(
            status.HTTP_400_BAD_REQUEST,
            "El límite debe ser un entero positivo",
        )

    try:
        respuesta = caso.ejecutar(q, limite_numerico)
    except ConsultaAutocompletarInvalidaError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except PersistenciaAutocompletarError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return AutocompletarUbicacionesResponseSchema(
        mensaje=respuesta.mensaje,
        data=AutocompletarUbicacionesDataSchema(
            consulta=respuesta.data.consulta,
            total=respuesta.data.total,
            sugerencias=[
                SugerenciaUbicacionItemSchema(
                    id=item.id,
                    nombre=item.nombre,
                    tipo=item.tipo,
                    departamento=item.departamento,
                )
                for item in respuesta.data.sugerencias
            ],
        ),
        success=respuesta.success,
    )


def _error(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"mensaje": mensaje, "data": None, "success": False},
    )