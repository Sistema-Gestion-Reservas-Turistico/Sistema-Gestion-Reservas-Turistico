from datetime import timedelta, timezone

from fastapi import APIRouter, Depends, Request, status
from app.api.responses import JSONResponse, api_error_response

from app.api.dependencies.usuarios import (
    obtener_caso_autenticar_usuario,
    obtener_repositorio_usuarios,
)
from app.api.dependencies.sesion import (
    obtener_caso_crear_sesion,
    obtener_caso_cerrar_sesion,
    obtener_caso_mantener_sesion,
    obtener_sesion_activa,
    obtener_token_bearer,
)
from app.api.schemas.autenticacion import (
    LoginErrorResponse,
    LoginExitosoData,
    LoginExitosoResponse,
    LoginRequestSchema,
    UsuarioAutenticadoData,
)
from app.api.schemas.sesion import (
    CerrarSesionApiResponse,
    CerrarSesionData,
    SesionActualApiResponse,
    SesionActualData,
    SesionErrorResponse,
    SesionInactivaErrorResponse,
    SesionRenovadaApiResponse,
    SesionRenovadaData,
)
from app.config import MINUTOS_INACTIVIDAD_SESION
from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.autenticacion import (
    CuentaBloqueadaTemporalmenteError,
    CuentaPendienteActivacionError,
    CredencialesInvalidasLoginError,
    PersistenciaSeguridadLoginError,
)
from app.services.use_cases.autenticar_usuario_con_bloqueo import (
    AutenticarUsuarioConBloqueoUseCase,
)
from app.services.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.services.use_cases.crear_sesion_usuario import CrearSesionUsuarioUseCase
from app.services.use_cases.mantener_sesion import MantenerSesionUseCase


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
                        "success": True,
                        "message": "Login successful",
                        "timestamp": "2026-11-26T12:00:00Z",
                        "errorCode": None,
                        "data": {
                            "token": "<signed-jwt>",
                            "token_type": "Bearer",
                            "expires_in": 1800,
                            "inactivity_timeout": 900,
                            "id": 101,
                            "nombres": "Laura",
                            "apellidos": "Gómez",
                            "correo": "laura.gomez@correo.com",
                            "rol": "Cliente",
                            "tipo": "Bearer",
                            "expira_en": 1800,
                            "inactividad_max": 900,
                            "user": {
                                "id": 101,
                                "first_name": "Laura",
                                "last_name": "Gómez",
                                "role": "Cliente",
                            },
                        },
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "model": LoginErrorResponse,
            "description": "Credenciales incorrectas.",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": LoginErrorResponse,
            "description": "Cuenta pendiente de activación.",
        },
        status.HTTP_423_LOCKED: {
            "model": LoginErrorResponse,
            "description": "Cuenta bloqueada temporalmente.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": LoginErrorResponse,
            "description": "Servicio no disponible.",
        },
    },
    summary="Iniciar sesión",
    description="Autentica al usuario y crea una sesión activa.",
)
def iniciar_sesion(
    solicitud: LoginRequestSchema,
    request: Request,
    caso: AutenticarUsuarioConBloqueoUseCase = Depends(
        obtener_caso_autenticar_usuario
    ),
    caso_sesion: CrearSesionUsuarioUseCase = Depends(obtener_caso_crear_sesion),
) -> LoginExitosoResponse | JSONResponse:
    ip_origen = _obtener_ip_origen(request)
    try:
        usuario = caso.ejecutar(solicitud.to_domain(), ip_origen)
    except CredencialesInvalidasLoginError as error:
        return _error(
            status.HTTP_401_UNAUTHORIZED,
            "The email or password is incorrect",
            {"attempts_remaining": error.intentos_restantes},
        )
    except CuentaBloqueadaTemporalmenteError as error:
        mensaje = (
            "Login for this email is temporarily locked after multiple failed "
            f"attempts. Try again in {error.minutos_restantes} minutes"
        )
        return _error(
            status.HTTP_423_LOCKED,
            mensaje,
            {
                "locked_until": error.bloqueada_hasta.astimezone(
                    timezone(timedelta(hours=-5), name="COT")
                ).isoformat(),
                "minutes_remaining": error.minutos_restantes,
            },
        )
    except CuentaPendienteActivacionError:
        return _error(
            status.HTTP_403_FORBIDDEN,
            "Activate your account using the link sent to your email",
        )
    except PersistenciaSeguridadLoginError:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "No fue posible iniciar sesión",
        )

    sesion = caso_sesion.ejecutar(usuario.id, usuario.correo, usuario.rol)
    return LoginExitosoResponse(
        message="Login successful",
        data=LoginExitosoData(
            token=sesion.token,
            token_type=sesion.tipo,
            expires_in=sesion.expira_en,
            inactivity_timeout=sesion.inactividad_max,
            id=usuario.id,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            correo=usuario.correo,
            rol=usuario.rol,
            tipo=sesion.tipo,
            expira_en=sesion.expira_en,
            inactividad_max=sesion.inactividad_max,
            user=UsuarioAutenticadoData(
                id=usuario.id,
                first_name=usuario.nombres,
                last_name=usuario.apellidos,
                role=usuario.rol,
            ),
        ),
        success=True,
    )


@router.get(
    "/me",
    response_model=SesionActualApiResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": SesionInactivaErrorResponse,
            "description": "Sesión inválida o inactiva.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": SesionErrorResponse,
            "description": "Validación de sesión no disponible.",
        },
    },
    summary="Consultar sesión actual",
)
def obtener_sesion_actual(
    sesion: SesionUsuario = Depends(obtener_sesion_activa),
    usuarios=Depends(obtener_repositorio_usuarios),
) -> SesionActualApiResponse | JSONResponse:
    usuario = usuarios.buscar_por_id(sesion.usuario_id)
    if usuario is None:
        return api_error_response(401, "Authentication is required", "UNAUTHORIZED")
    return SesionActualApiResponse(
        success=True,
        message="Current session retrieved successfully",
        data=SesionActualData(
            user_id=sesion.usuario_id,
            email=sesion.correo,
            role=sesion.rol,
            started_at=sesion.inicio_en,
            last_activity=sesion.ultima_actividad,
            inactivity_timeout=MINUTOS_INACTIVIDAD_SESION * 60,
            user=UsuarioAutenticadoData(
                id=usuario.id,
                first_name=usuario.nombres,
                last_name=usuario.apellidos,
                role=usuario.rol,
            ),
        ),
    )


@router.post(
    "/sesion/mantener",
    response_model=SesionRenovadaApiResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": SesionInactivaErrorResponse,
            "description": "Token inválido o sesión cerrada.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": SesionErrorResponse,
            "description": "Validación de sesión no disponible.",
        },
    },
    summary="Mantener sesión",
    description="Renueva el token y actualiza la última actividad.",
)
def mantener_sesion(
    token: str = Depends(obtener_token_bearer),
    caso: MantenerSesionUseCase = Depends(obtener_caso_mantener_sesion),
) -> SesionRenovadaApiResponse:
    renovada = caso.ejecutar(token)
    return SesionRenovadaApiResponse(
        success=True,
        message="Session renewed successfully",
        data=SesionRenovadaData(
            token=renovada.token,
            token_type=renovada.tipo,
            expires_in=renovada.expira_en,
            inactivity_timeout=renovada.inactividad_max,
        ),
    )


@router.post(
    "/logout",
    response_model=CerrarSesionApiResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": SesionInactivaErrorResponse,
            "description": "Token inválido o sesión cerrada.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": SesionErrorResponse,
            "description": "Validación de sesión no disponible.",
        },
    },
    summary="Cerrar sesión",
)
def cerrar_sesion(
    token: str = Depends(obtener_token_bearer),
    caso: CerrarSesionUseCase = Depends(obtener_caso_cerrar_sesion),
) -> CerrarSesionApiResponse:
    cerrada = caso.ejecutar(token)
    return CerrarSesionApiResponse(
        success=True,
        message="Session closed successfully",
        data=CerrarSesionData(
            message="Session closed successfully",
            close_reason=cerrada.motivo_cierre,
            closed_at=cerrada.cerrada_en,
        ),
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
