from datetime import timedelta, timezone

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies.usuarios import obtener_caso_autenticar_usuario
from app.api.schemas.autenticacion import (
    LoginErrorResponse,
    LoginExitosoData,
    LoginExitosoResponse,
    LoginRequestSchema,
)
from app.domain.exceptions.autenticacion import (
    CuentaBloqueadaTemporalmenteError,
    CuentaPendienteActivacionError,
    CredencialesInvalidasLoginError,
    PersistenciaSeguridadLoginError,
)
from app.services.use_cases.autenticar_usuario_con_bloqueo import (
    AutenticarUsuarioConBloqueoUseCase,
)


router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginExitosoResponse,
    responses={
        status.HTTP_200_OK: {
            "model": LoginExitosoResponse,
            "description": "Autenticación exitosa para una cuenta activa.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Inicio de sesión exitoso",
                        "data": {
                            "id": 101,
                            "nombres": "Laura",
                            "apellidos": "Gómez",
                            "correo": "laura.gomez@correo.com",
                            "rol": "Cliente",
                        },
                        "success": True,
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": LoginErrorResponse,
            "description": "Correo o contraseña incorrectos.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "Correo o contraseña incorrectos",
                        "data": {"intentos_restantes": 2},
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "model": LoginErrorResponse,
            "description": "La cuenta aún no ha sido activada.",
        },
        status.HTTP_423_LOCKED: {
            "model": LoginErrorResponse,
            "description": "La cuenta se bloqueó temporalmente por intentos fallidos.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": (
                            "El inicio de sesión con este correo está bloqueado "
                            "temporalmente por varios intentos fallidos. Intenta de "
                            "nuevo en 15 minutos"
                        ),
                        "data": {
                            "bloqueada_hasta": "2026-11-17T11:30:00-05:00",
                            "minutos_restantes": 15,
                        },
                        "success": False,
                    }
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": LoginErrorResponse,
            "description": "No fue posible consultar o guardar el estado de seguridad.",
            "content": {
                "application/json": {
                    "example": {
                        "mensaje": "No fue posible iniciar sesión",
                        "data": None,
                        "success": False,
                    }
                }
            },
        },
    },
    summary="Iniciar sesión",
    description=(
        "Autentica una cuenta activa y registra eventos de seguridad. Tras "
        "MAX_INTENTOS_FALLIDOS_LOGIN intentos fallidos (por defecto 5), la cuenta "
        "queda bloqueada durante MINUTOS_BLOQUEO_LOGIN (por defecto 15). El "
        "contador se reinicia al expirar el bloqueo, al transcurrir el periodo "
        "sin nuevos intentos o tras credenciales correctas. El control es "
        "independiente de si el correo está registrado. Para cuentas existentes "
        "se envía una sola notificación por bloqueo. Ejemplo del correo: "
        "Asunto: Bloqueo temporal de tu cuenta.\n\n"
        "Hola Laura,\n"
        "Detectamos varios intentos fallidos de inicio de sesión en tu cuenta y "
        "la bloqueamos temporalmente por seguridad.\n"
        "Bloqueo: 17/11/2026 11:15\n"
        "Podrás volver a intentarlo a las 11:30.\n"
        "Si fuiste tú, espera a que termine el bloqueo e ingresa con tu contraseña. "
        "Si no reconoces esta actividad, comunícate con nosotros."
    ),
)
def iniciar_sesion(
    solicitud: LoginRequestSchema,
    request: Request,
    caso: AutenticarUsuarioConBloqueoUseCase = Depends(
        obtener_caso_autenticar_usuario
    ),
) -> LoginExitosoResponse | JSONResponse:
    ip_origen = _obtener_ip_origen(request)
    try:
        usuario = caso.ejecutar(solicitud.to_domain(), ip_origen)
    except CredencialesInvalidasLoginError as error:
        return _error(
            status.HTTP_401_UNAUTHORIZED,
            "Correo o contraseña incorrectos",
            {"intentos_restantes": error.intentos_restantes},
        )
    except CuentaBloqueadaTemporalmenteError as error:
        mensaje = (
            "El inicio de sesión con este correo está bloqueado temporalmente por "
            "varios intentos fallidos. Intenta de nuevo en "
            f"{error.minutos_restantes} minutos"
        )
        return _error(
            status.HTTP_423_LOCKED,
            mensaje,
            {
                "bloqueada_hasta": error.bloqueada_hasta.astimezone(
                    timezone(timedelta(hours=-5), name="COT")
                ).isoformat(),
                "minutos_restantes": error.minutos_restantes,
            },
        )
    except CuentaPendienteActivacionError as error:
        return _error(status.HTTP_403_FORBIDDEN, str(error))
    except PersistenciaSeguridadLoginError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No fue posible iniciar sesión",
        )

    return LoginExitosoResponse(
        mensaje="Inicio de sesión exitoso",
        data=LoginExitosoData(
            id=usuario.id,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            correo=usuario.correo,
            rol=usuario.rol,
        ),
        success=True,
    )


def _obtener_ip_origen(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip = forwarded_for.split(",", maxsplit=1)[0].strip()
        if ip:
            return ip
    return request.client.host if request.client is not None else None


def _error(
    codigo: int, mensaje: str, data: dict[str, int | str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje, "data": data, "success": False},
    )
