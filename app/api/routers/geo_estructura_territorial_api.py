from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies.autorizacion import autorizar_administrador_jwt
from app.api.dependencies.destinos import (
    obtener_caso_consultar_estructura_territorial,
)
from app.api.schemas.estructura_territorial import (
    DepartamentoEstructuraItemSchema,
    EstructuraTerritorialDataSchema,
    EstructuraTerritorialResponseSchema,
    ErrorEstructuraTerritorialResponseSchema,
    MunicipioEstructuraItemSchema,
)
from app.domain.exceptions.estructura_territorial import (
    ParametrosEstructuraInvalidosError,
    PersistenciaEstructuraTerritorialError,
)
from app.services.use_cases.consultar_estructura_territorial import (
    ConsultarEstructuraTerritorialUseCase,
)


router = APIRouter(prefix="/api/v1/geo/ubicaciones", tags=["Geografía"])


def _ejemplo_error(mensaje: str) -> dict:
    return {"mensaje": mensaje, "data": None, "success": False}


@router.get(
    "/estructura",
    response_model=EstructuraTerritorialResponseSchema,
    response_model_exclude_none=True,
    responses={
        status.HTTP_200_OK: {
            "model": EstructuraTerritorialResponseSchema,
            "description": "Estructura territorial encontrada o sin resultados.",
            "content": {
                "application/json": {
                    "examples": {
                        "estructura": {
                            "summary": "Estructura de Quindío con todos sus municipios",
                            "value": {
                                "mensaje": "Consulta de estructura territorial exitosa",
                                "data": {
                                    "id_pais": 1,
                                    "nombre": "Colombia",
                                    "total_departamentos": 1,
                                    "total_municipios": 3,
                                    "departamentos": [
                                        {
                                            "id": 63,
                                            "nombre": "Quindío",
                                            "municipios": [
                                                {
                                                    "id": 63001,
                                                    "nombre": "Armenia",
                                                    "habilitado": True,
                                                },
                                                {
                                                    "id": 63130,
                                                    "nombre": "Calarcá",
                                                    "habilitado": False,
                                                },
                                                {
                                                    "id": 63690,
                                                    "nombre": "Salento",
                                                    "habilitado": True,
                                                },
                                            ],
                                        }
                                    ],
                                },
                                "success": True,
                            },
                        },
                        "sin_estructura": {
                            "summary": "País sin estructura territorial",
                            "value": {
                                "mensaje": (
                                    "No existe estructura territorial para el país indicado"
                                ),
                                "data": {
                                    "id_pais": 9999,
                                    "total_departamentos": 0,
                                    "total_municipios": 0,
                                    "departamentos": [],
                                },
                                "success": False,
                            },
                        },
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorEstructuraTerritorialResponseSchema,
            "description": "El identificador del país o departamento es inválido.",
            "content": {
                "application/json": {
                    "examples": {
                        "pais": {
                            "value": _ejemplo_error(
                                "El identificador del país es obligatorio y debe ser numérico"
                            )
                        },
                        "departamento": {
                            "value": _ejemplo_error(
                                "El identificador del departamento debe ser numérico"
                            )
                        },
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": ErrorEstructuraTerritorialResponseSchema,
            "description": "Token JWT requerido o inválido.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error("Authentication is required")
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorEstructuraTerritorialResponseSchema,
            "description": "Se requiere rol Administrador.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No tiene permisos para realizar esta acción"
                    )
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorEstructuraTerritorialResponseSchema,
            "description": "Consulta no disponible.",
            "content": {
                "application/json": {
                    "example": _ejemplo_error(
                        "No fue posible consultar la estructura territorial"
                    )
                }
            },
        },
    },
    summary="Consultar estructura territorial",
    description=(
        "Consulta un país y sus departamentos con todos sus municipios, "
        "incluidos los inhabilitados. `id_pais` es obligatorio; "
        "`id_departamento` limita la consulta a un departamento perteneciente "
        "a ese país. Requiere un JWT válido con rol Administrador."
    ),
)
def consultar_estructura_territorial(
    id_pais: str | None = Query(
        default=None, description="Identificador numérico obligatorio del país."
    ),
    id_departamento: str | None = Query(
        default=None,
        description="Identificador numérico opcional de departamento.",
    ),
    _: None = Depends(autorizar_administrador_jwt),
    caso: ConsultarEstructuraTerritorialUseCase = Depends(
        obtener_caso_consultar_estructura_territorial
    ),
) -> EstructuraTerritorialResponseSchema | JSONResponse:
    try:
        respuesta = caso.ejecutar(id_pais, id_departamento)
    except ParametrosEstructuraInvalidosError as error:
        return _error(status.HTTP_400_BAD_REQUEST, str(error))
    except PersistenciaEstructuraTerritorialError as error:
        return _error(status.HTTP_503_SERVICE_UNAVAILABLE, str(error))

    return EstructuraTerritorialResponseSchema(
        mensaje=respuesta.mensaje,
        data=EstructuraTerritorialDataSchema(
            id_pais=respuesta.data.id_pais,
            nombre=respuesta.data.nombre,
            total_departamentos=respuesta.data.total_departamentos,
            total_municipios=respuesta.data.total_municipios,
            departamentos=[
                DepartamentoEstructuraItemSchema(
                    id=departamento.id,
                    nombre=departamento.nombre,
                    municipios=[
                        MunicipioEstructuraItemSchema(
                            id=municipio.id,
                            nombre=municipio.nombre,
                            habilitado=municipio.habilitado,
                        )
                        for municipio in departamento.municipios
                    ],
                )
                for departamento in respuesta.data.departamentos
            ],
        ),
        success=respuesta.success,
    )


def _error(status_code: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"mensaje": mensaje, "data": None, "success": False},
    )
