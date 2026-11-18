import os


MAX_INTENTOS_FALLIDOS_LOGIN = int(os.getenv("MAX_INTENTOS_FALLIDOS_LOGIN", "5"))
MINUTOS_BLOQUEO_LOGIN = int(os.getenv("MINUTOS_BLOQUEO_LOGIN", "15"))

if MAX_INTENTOS_FALLIDOS_LOGIN < 1:
    raise ValueError("MAX_INTENTOS_FALLIDOS_LOGIN debe ser mayor que cero")
if MINUTOS_BLOQUEO_LOGIN < 1:
    raise ValueError("MINUTOS_BLOQUEO_LOGIN debe ser mayor que cero")
