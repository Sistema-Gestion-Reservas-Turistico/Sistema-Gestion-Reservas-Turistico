from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.api.dependencies.usuarios import obtener_caso_registrar_usuario
from app.api.schemas.usuarios import (
    ErrorRegistroResponse,
    UsuarioRegistroData,
    UsuarioRegistroRequest,
    UsuarioRegistroResponse,
)
from app.domain.exceptions.usuarios import (
    CorreoDuplicadoError,
    DatosRegistroInvalidosError,
    DocumentoDuplicadoError,
    PersistenciaUsuariosError,
    TratamientoDatosNoAceptadoError,
)
from app.services.use_cases.registrar_usuario import RegistrarUsuarioUseCase


router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.post(
    "/registro",
    status_code=status.HTTP_201_CREATED,
    response_model=UsuarioRegistroResponse,
    responses={
        status.HTTP_201_CREATED: {
            "model": UsuarioRegistroResponse,
            "description": "Cuenta creada y pendiente de activación por correo.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": (
                            "Registro exitoso. Revisa tu correo para activar tu cuenta"
                        ),
                        "data": {
                            "id": 101,
                            "nombres": "Laura",
                            "apellidos": "Gómez",
                            "correo": "laura.gomez@correo.com",
                            "estado": "PENDIENTE_ACTIVACION",
                        },
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorRegistroResponse,
            "description": "Los campos de registro no son válidos.",
            "content": {
                "application/json": {
                    "examples": {
                        "validacion": {
                            "summary": "Error de validación",
                            "value": {
                                "mensaje": "Los datos de registro no son válidos",
                                "data": {
                                    "errores": [
                                        {
                                            "campo": "correo",
                                            "detalle": "Debe ser un correo válido",
                                        }
                                    ]
                                },
                                "success": False,
                            },
                        },
                        "tratamiento_datos": {
                            "summary": "Tratamiento de datos no aceptado",
                            "value": {
                                "mensaje": (
                                    "Debes aceptar el tratamiento de datos personales "
                                    "para registrarte"
                                ),
                                "data": {
                                    "errores": [
                                        {
                                            "campo": "acepta_tratamiento_datos",
                                            "detalle": (
                                                "Debes aceptar el tratamiento de datos "
                                                "personales para registrarte"
                                            ),
                                        }
                                    ]
                                },
                                "success": False,
                            },
                        },
                    }
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "model": ErrorRegistroResponse,
            "description": "El correo o el documento ya están registrados.",
            "content": {
                "application/json": {
                    "examples": {
                        "correo_duplicado": {
                            "value": {
                                "mensaje": "Ya existe una cuenta con el correo indicado",
                                "data": None,
                                "success": False,
                            }
                        },
                        "documento_duplicado": {
                            "value": {
                                "mensaje": "Ya existe una cuenta con el documento indicado",
                                "data": None,
                                "success": False,
                            }
                        },
                    }
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ErrorRegistroResponse,
            "description": "No fue posible guardar el registro.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "No fue posible completar el registro",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
    },
    summary="Registrar una cuenta de usuario",
    description=(
        "Registra una cuenta pública sin sesión. Valida que el tipo de documento "
        "esté activo en TIPO_DOCUMENTO, que el documento y el correo sean únicos, "
        "que el correo tenga formato válido, que la contraseña tenga al menos "
        "8 caracteres con mayúscula, minúscula y número, y que se acepte el "
        "tratamiento de datos. El rol siempre se asigna como Cliente y el estado "
        "inicial como PENDIENTE_ACTIVACION."
    ),
)
def registrar_usuario(
    solicitud: UsuarioRegistroRequest,
    caso: RegistrarUsuarioUseCase = Depends(obtener_caso_registrar_usuario),
) -> UsuarioRegistroResponse | JSONResponse:
    try:
        registro = caso.ejecutar(solicitud.to_domain())
    except TratamientoDatosNoAceptadoError as error:
        detalle = str(error)
        return _error(
            status.HTTP_400_BAD_REQUEST,
            detalle,
            [{"campo": "acepta_tratamiento_datos", "detalle": detalle}],
        )
    except DatosRegistroInvalidosError as error:
        return _error(
            status.HTTP_400_BAD_REQUEST,
            "Los datos de registro no son válidos",
            [
                {"campo": item.campo, "detalle": item.detalle}
                for item in error.errores
            ],
        )
    except CorreoDuplicadoError:
        return _error(
            status.HTTP_409_CONFLICT,
            "Ya existe una cuenta con el correo indicado",
        )
    except DocumentoDuplicadoError:
        return _error(
            status.HTTP_409_CONFLICT,
            "Ya existe una cuenta con el documento indicado",
        )
    except PersistenciaUsuariosError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No fue posible completar el registro",
        )

    return UsuarioRegistroResponse(
        mensaje="Registro exitoso. Revisa tu correo para activar tu cuenta",
        data=UsuarioRegistroData(
            id=registro.id,
            nombres=registro.nombres,
            apellidos=registro.apellidos,
            correo=registro.correo,
            estado=registro.estado,
        ),
        success=True,
    )


def _error(
    codigo: int,
    mensaje: str,
    errores: list[dict[str, str]] | None = None,
) -> JSONResponse:
    data = {"errores": errores} if errores is not None else None
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje, "data": data, "success": False},
    )
