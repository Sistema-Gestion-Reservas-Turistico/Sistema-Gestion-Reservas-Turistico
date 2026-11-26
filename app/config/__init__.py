import os


MAX_INTENTOS_FALLIDOS_LOGIN = int(os.getenv("MAX_INTENTOS_FALLIDOS_LOGIN", "5"))
MINUTOS_BLOQUEO_LOGIN = int(os.getenv("MINUTOS_BLOQUEO_LOGIN", "15"))
HORAS_VIGENCIA_TOKEN_ACTIVACION = int(
    os.getenv("HORAS_VIGENCIA_TOKEN_ACTIVACION", "24")
)
MAX_REENVIOS_ACTIVACION_POR_HORA = int(
    os.getenv("MAX_REENVIOS_ACTIVACION_POR_HORA", "3")
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "local-development-secret-change-before-deploy"
)
MINUTOS_EXPIRACION_JWT = int(os.getenv("MINUTOS_EXPIRACION_JWT", "60"))

if MAX_INTENTOS_FALLIDOS_LOGIN < 1:
    raise ValueError("MAX_INTENTOS_FALLIDOS_LOGIN debe ser mayor que cero")
if MINUTOS_BLOQUEO_LOGIN < 1:
    raise ValueError("MINUTOS_BLOQUEO_LOGIN debe ser mayor que cero")
if HORAS_VIGENCIA_TOKEN_ACTIVACION < 1:
    raise ValueError("HORAS_VIGENCIA_TOKEN_ACTIVACION debe ser mayor que cero")
if MAX_REENVIOS_ACTIVACION_POR_HORA < 1:
    raise ValueError("MAX_REENVIOS_ACTIVACION_POR_HORA debe ser mayor que cero")
if len(JWT_SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")
if MINUTOS_EXPIRACION_JWT < 1:
    raise ValueError("MINUTOS_EXPIRACION_JWT debe ser mayor que cero")
