from fastapi import APIRouter, Depends, status
from app.api.responses import JSONResponse

from app.api.dependencies.usuarios import (
    obtener_caso_activar_cuenta,
    obtener_caso_registrar_usuario,
    obtener_caso_reenviar_activacion,
)
from app.api.schemas.activacion import (
    ActivacionErrorResponse,
    ActivarCuentaData,
    ActivarCuentaRequestSchema,
    ActivarCuentaResponseSchema,
    ReenviarActivacionRequestSchema,
    ReenviarActivacionResponseSchema,
)
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
from app.domain.exceptions.activacion import (
    CuentaYaActivaError,
    LimiteReenviosActivacionError,
    PersistenciaActivacionError,
    TokenActivacionInvalidoError,
    TokenActivacionVencidoError,
)
from app.domain.models.activacion import ReenviarActivacionRequest
from app.services.use_cases.activar_cuenta_por_token import (
    ActivarCuentaPorTokenUseCase,
)
from app.services.use_cases.reenviar_activacion_cuenta import (
    ReenviarActivacionCuentaUseCase,
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
    except TratamientoDatosNoAceptadoError:
        detalle = "You must accept the personal data processing terms to register"
        return _error(
            status.HTTP_400_BAD_REQUEST,
            detalle,
            [{"campo": "acepta_tratamiento_datos", "detalle": detalle}],
        )
    except DatosRegistroInvalidosError as error:
        return _error(
            status.HTTP_400_BAD_REQUEST,
            "Registration data is invalid",
            [
                {"campo": item.campo, "detalle": item.detalle}
                for item in error.errores
            ],
        )
    except CorreoDuplicadoError:
        return _error(
            status.HTTP_409_CONFLICT,
            "An account with this email already exists",
        )
    except DocumentoDuplicadoError:
        return _error(
            status.HTTP_409_CONFLICT,
            "An account with this document already exists",
        )
    except PersistenciaUsuariosError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Unable to complete the registration",
        )

    return UsuarioRegistroResponse(
        message="Registration successful. Check your email to activate your account",
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


@router.post(
    "/activacion",
    status_code=status.HTTP_200_OK,
    response_model=ActivarCuentaResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": ActivarCuentaResponseSchema,
            "description": "La cuenta fue activada.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Account activated successfully",
                        "data": {
                            "id": 101,
                            "correo": "laura.gomez@correo.com",
                            "estado": "ACTIVA",
                        },
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ActivacionErrorResponse,
            "description": "El enlace de activación no existe o fue invalidado.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "The activation link is invalid",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_409_CONFLICT: {
            "model": ActivacionErrorResponse,
            "description": "La cuenta ya fue activada.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "The account is already active",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_410_GONE: {
            "model": ActivacionErrorResponse,
            "description": "El enlace de activación venció.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "The activation link has expired. Request a new one",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ActivacionErrorResponse,
            "description": "No fue posible consultar o actualizar la cuenta.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Unable to process the activation request",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
    },
    summary="Activar una cuenta con el enlace enviado por correo",
    description=(
        "Consume un token de un solo uso enviado por correo. El registro y el "
        "reenvío construyen el enlace como "
        "`{FRONTEND_URL}/activar-cuenta?token={token}`; el token original no se "
        "almacena. Los tokens vencen según HORAS_VIGENCIA_TOKEN_ACTIVACION "
        "(24 horas por defecto)."
    ),
)
def activar_cuenta(
    solicitud: ActivarCuentaRequestSchema,
    caso: ActivarCuentaPorTokenUseCase = Depends(obtener_caso_activar_cuenta),
) -> ActivarCuentaResponseSchema | JSONResponse:
    try:
        cuenta = caso.ejecutar(solicitud.to_domain())
    except TokenActivacionInvalidoError:
        return _error_activacion(
            status.HTTP_400_BAD_REQUEST, "The activation link is invalid"
        )
    except CuentaYaActivaError:
        return _error_activacion(status.HTTP_409_CONFLICT, "The account is already active")
    except TokenActivacionVencidoError:
        return _error_activacion(
            status.HTTP_410_GONE,
            "The activation link has expired. Request a new one",
        )
    except PersistenciaActivacionError:
        return _error_activacion(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Unable to process the activation request",
        )

    return ActivarCuentaResponseSchema(
        message="Account activated successfully",
        data=ActivarCuentaData(
            id=cuenta.id,
            correo=cuenta.correo,
            estado=cuenta.estado,
        ),
        success=True,
    )


@router.post(
    "/activacion/reenviar",
    status_code=status.HTTP_200_OK,
    response_model=ReenviarActivacionResponseSchema,
    responses={
        status.HTTP_200_OK: {
            "model": ReenviarActivacionResponseSchema,
            "description": (
                "Respuesta idéntica exista o no una cuenta pendiente para el correo."
            ),
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": (
                            "Si el correo corresponde a una cuenta pendiente, "
                            "enviaremos un nuevo enlace"
                        ),
                        "data": None,
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ActivacionErrorResponse,
            "description": "Se alcanzó el límite horario de reenvíos.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Too many requests. Try again later",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ActivacionErrorResponse,
            "description": "No fue posible consultar o guardar la solicitud.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Unable to process the activation request",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
    },
    summary="Reenviar el enlace de activación",
    description=(
        "Solicita un enlace nuevo para una cuenta pendiente. Por privacidad, "
        "la respuesta es idéntica cuando el correo no existe o la cuenta ya "
        "está activa. El límite es MAX_REENVIOS_ACTIVACION_POR_HORA (3 por "
        "correo en una hora, por defecto)."
    ),
)
def reenviar_activacion(
    solicitud: ReenviarActivacionRequestSchema,
    caso: ReenviarActivacionCuentaUseCase = Depends(
        obtener_caso_reenviar_activacion
    ),
) -> ReenviarActivacionResponseSchema | JSONResponse:
    try:
        resultado = caso.ejecutar(
            ReenviarActivacionRequest(correo=str(solicitud.correo))
        )
    except LimiteReenviosActivacionError:
        return _error_activacion(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many requests. Try again later",
        )
    except PersistenciaActivacionError:
        return _error_activacion(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Unable to process the activation request",
        )
    return ReenviarActivacionResponseSchema(
        message="If the email matches a pending account, we will send a new link",
        data=None,
        success=True,
    )


def _error_activacion(codigo: int, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje, "data": None, "success": False},
    )
