from datetime import datetime, timezone
from typing import Generic, Literal, TypeVar

from fastapi.responses import JSONResponse as FastAPIJSONResponse
from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


def utc_timestamp() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool
    message: str
    timestamp: str = Field(
        default_factory=utc_timestamp,
        json_schema_extra={
            "format": "date-time",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
    )
    errorCode: str | None = None
    data: DataT


class ApiErrorResponse(ApiResponse[object | None]):
    success: Literal[False] = False
    errorCode: str
    data: object | None = None


def error_code_for_status(status_code: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        410: "GONE",
        422: "VALIDATION_ERROR",
        423: "ACCOUNT_LOCKED",
        429: "TOO_MANY_REQUESTS",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE",
    }.get(status_code, f"HTTP_{status_code}")


def error_code_for_message(message: str, status_code: int) -> str:
    return {
        "A category with the specified key already exists": "CATEGORY_ALREADY_EXISTS",
        "The specified category was not found": "CATEGORY_NOT_FOUND",
        "The specified category does not exist": "CATEGORY_NOT_FOUND",
        "A value with the specified code already exists in this category":
            "CATEGORY_VALUE_ALREADY_EXISTS",
        "The specified value does not exist in this category":
            "CATEGORY_VALUE_NOT_FOUND",
        "The specified value was not found": "CATEGORY_VALUE_NOT_FOUND",
        "This value is required by the system and cannot be deactivated":
            "SYSTEM_VALUE_CANNOT_BE_DEACTIVATED",
        "At least one payment method must remain active":
            "LAST_ACTIVE_PAYMENT_METHOD",
        "The email or password is incorrect": "INVALID_CREDENTIALS",
        "The account has not been activated": "ACCOUNT_NOT_ACTIVATED",
        "Activate your account using the link sent to your email":
            "ACCOUNT_NOT_ACTIVATED",
        "The account is temporarily locked": "ACCOUNT_TEMPORARILY_LOCKED",
        "An account with this email already exists": "EMAIL_ALREADY_REGISTERED",
        "An account with this document already exists": "DOCUMENT_ALREADY_REGISTERED",
        "The activation link is invalid": "INVALID_ACTIVATION_TOKEN",
        "The activation link has expired. Request a new one": "ACTIVATION_TOKEN_EXPIRED",
        "The account is already active": "ACCOUNT_ALREADY_ACTIVE",
        "Tu sesión se cerró por inactividad. Inicia sesión de nuevo":
            "SESION_INACTIVA",
    }.get(message, error_code_for_status(status_code))


def english_error_message(message: str, status_code: int) -> str:
    translations = {
        "Categorías consultadas correctamente": "Categories retrieved successfully",
        "Categoría guardada correctamente": "Category saved successfully",
        "Valores consultados correctamente": "Category values retrieved successfully",
        "Valor guardado correctamente": "Category value saved successfully",
        "Estado del valor actualizado correctamente":
            "Category value status updated successfully",
        "Consulta de parámetros de pagos exitosa":
            "Payment parameters retrieved successfully",
        "Parámetros de transporte consultados correctamente":
            "Transportation parameters retrieved successfully",
        "Consulta de parámetros exitosa": "Parameters retrieved successfully",
        "Consulta de parámetro exitosa": "Parameter retrieved successfully",
        "Consulta de parámetros de alojamiento y alimentación exitosa":
            "Accommodation and meal parameters retrieved successfully",
        "Inicio de sesión exitoso": "Login successful",
        "Registro exitoso. Revisa tu correo para activar tu cuenta":
            "Registration successful. Check your email to activate your account",
        "Cuenta activada correctamente": "Account activated successfully",
        "Si el correo corresponde a una cuenta pendiente, enviaremos un nuevo enlace":
            "If the email matches a pending account, we will send a new link",
        "Ya existe una categoría con la clave indicada":
            "A category with the specified key already exists",
        "Debe indicar el nombre o la descripción para actualizar":
            "Provide a name or description to update the category",
        "No se encontró la categoría indicada": "The specified category was not found",
        "Ya existe un valor con el código indicado en esta categoría":
            "A value with the specified code already exists in this category",
        "Debe indicar nombre, descripción u orden para actualizar":
            "Provide a name, description, or order to update the value",
        "El valor indicado no existe en esta categoría":
            "The specified value does not exist in this category",
        "Este valor es requerido por el sistema y no se puede inactivar":
            "This value is required by the system and cannot be deactivated",
        "Debe existir al menos un método de pago activo":
            "At least one payment method must remain active",
        "El valor indicado no existe": "The specified value was not found",
        "No fue posible consultar los parámetros de pagos":
            "Payment parameters could not be retrieved",
        "No se encontraron las categorías de transporte iniciales":
            "The initial transportation categories were not found",
        "La categoría indicada no existe": "The specified category does not exist",
        "No fue posible consultar los parámetros": "Parameters could not be retrieved",
        "El parámetro no existe o no está vigente":
            "The parameter does not exist or is no longer active",
        "No tiene permisos para realizar esta acción":
            "You are not authorized to perform this action",
        "No fue posible consultar los parámetros de alojamiento y alimentación":
            "Accommodation and meal parameters could not be retrieved",
        "Correo o contraseña incorrectos": "The email or password is incorrect",
        "No fue posible iniciar sesión": "Unable to sign in at this time",
        "Los datos de registro no son válidos": "Registration data is invalid",
        "Ya existe una cuenta con el correo indicado":
            "An account with this email already exists",
        "Ya existe una cuenta con el documento indicado":
            "An account with this document already exists",
        "No fue posible completar el registro": "Unable to complete the registration",
        "El enlace de activación no es válido": "The activation link is invalid",
        "La cuenta ya está activa": "The account is already active",
        "El enlace de activación venció. Solicita uno nuevo":
            "The activation link has expired. Request a new one",
        "No fue posible procesar la activación":
            "Unable to process the activation request",
        "Demasiadas solicitudes. Intenta de nuevo más tarde":
            "Too many requests. Try again later",
        "Tu sesión se cerró por inactividad. Inicia sesión de nuevo":
            "Tu sesión se cerró por inactividad. Inicia sesión de nuevo",
        "La sesión es inválida, venció o ya fue cerrada":
            "The session is invalid, expired or closed",
        "No fue posible validar la sesión": "No fue posible validar la sesión",
    }
    if message in translations:
        return translations[message]

    spanish_markers = (
        "á", "é", "í", "ó", "ú", "ñ", "acción", "cuenta", "correo",
        "categoría", "parámetro", "indicado", "debe ", "no fue", "ya existe",
    )
    if any(marker in message.casefold() for marker in spanish_markers):
        if status_code < 400:
            return "Request completed successfully"
        return {
            400: "The request is invalid",
            401: "The email or password is incorrect",
            403: "Administrator access is required",
            404: "The requested resource was not found",
            409: "The request conflicts with the current resource state",
            410: "The requested resource has expired",
            423: "The account is temporarily locked",
            429: "Too many requests. Try again later",
            503: "The service is temporarily unavailable",
        }.get(status_code, "The request failed")
    return message


def api_error_response(
    status_code: int,
    message: str,
    error_code: str | None = None,
    data: object | None = None,
) -> "JSONResponse":
    body = ApiErrorResponse(
        success=False,
        message=english_error_message(message, status_code),
        errorCode=error_code or error_code_for_message(
            english_error_message(message, status_code), status_code
        ),
        data=data,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


class JSONResponse(FastAPIJSONResponse):
    def __init__(self, content, status_code: int = 200, **kwargs):
        if isinstance(content, dict):
            success = bool(content.get("success", status_code < 400))
            message = content.get("message", content.get("mensaje"))
            timestamp = content.get("timestamp") or utc_timestamp()
            data = content.get("data")
            error_code = content.get("errorCode")

            if not isinstance(message, str):
                detail = content.get("detail")
                message = detail if isinstance(detail, str) else (
                    "The request failed" if not success else "Request completed successfully"
                )

            message = english_error_message(message, status_code)

            if success:
                envelope = ApiResponse[
                    object
                ](
                    success=True,
                    message=message,
                    timestamp=timestamp,
                    errorCode=error_code,
                    data=data,
                )
            else:
                codigo_error = error_code or error_code_for_message(
                    message, status_code
                )
                envelope = ApiErrorResponse(
                    success=False,
                    message=message,
                    timestamp=timestamp,
                    errorCode=codigo_error,
                    data=data if codigo_error == "SESION_INACTIVA" else None,
                )
            content = envelope.model_dump()

        super().__init__(content=content, status_code=status_code, **kwargs)
