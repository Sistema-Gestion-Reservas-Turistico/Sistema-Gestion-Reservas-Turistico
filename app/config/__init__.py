import os


MAX_INTENTOS_FALLIDOS_LOGIN = int(os.getenv("MAX_INTENTOS_FALLIDOS_LOGIN", "5"))
MINUTOS_BLOQUEO_LOGIN = int(os.getenv("MINUTOS_BLOQUEO_LOGIN", "15"))
HORAS_VIGENCIA_TOKEN_ACTIVACION = int(
    os.getenv("HORAS_VIGENCIA_TOKEN_ACTIVACION", "24")
)
MAX_REENVIOS_ACTIVACION_POR_HORA = int(
    os.getenv("MAX_REENVIOS_ACTIVACION_POR_HORA", "3")
)
MINUTOS_INACTIVIDAD_SESION = int(os.getenv("MINUTOS_INACTIVIDAD_SESION", "15"))
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "local-development-secret-change-before-deploy"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
MINUTOS_EXPIRACION_TOKEN = int(
    os.getenv(
        "MINUTOS_EXPIRACION_TOKEN",
        os.getenv("MINUTOS_EXPIRACION_JWT", "30"),
    )
)
MINUTOS_EXPIRACION_JWT = int(
    os.getenv("MINUTOS_EXPIRACION_JWT", str(MINUTOS_EXPIRACION_TOKEN))
)

if MAX_INTENTOS_FALLIDOS_LOGIN < 1:
    raise ValueError("MAX_INTENTOS_FALLIDOS_LOGIN debe ser mayor que cero")
if MINUTOS_BLOQUEO_LOGIN < 1:
    raise ValueError("MINUTOS_BLOQUEO_LOGIN debe ser mayor que cero")
if HORAS_VIGENCIA_TOKEN_ACTIVACION < 1:
    raise ValueError("HORAS_VIGENCIA_TOKEN_ACTIVACION debe ser mayor que cero")
if MAX_REENVIOS_ACTIVACION_POR_HORA < 1:
    raise ValueError("MAX_REENVIOS_ACTIVACION_POR_HORA debe ser mayor que cero")
if MINUTOS_INACTIVIDAD_SESION < 1:
    raise ValueError("MINUTOS_INACTIVIDAD_SESION debe ser mayor que cero")
if MINUTOS_EXPIRACION_TOKEN < 1:
    raise ValueError("MINUTOS_EXPIRACION_TOKEN debe ser mayor que cero")
if len(JWT_SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
if MINUTOS_EXPIRACION_JWT < 1:
    raise ValueError("MINUTOS_EXPIRACION_JWT debe ser mayor que cero")
