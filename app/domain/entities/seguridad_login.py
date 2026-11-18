from dataclasses import dataclass
from datetime import datetime
from typing import Literal


TipoEventoSeguridadLogin = Literal[
    "INTENTO_FALLIDO", "BLOQUEO_CUENTA", "LOGIN_EXITOSO"
]


@dataclass(frozen=True)
class EstadoIntentosLogin:
    correo_normalizado: str
    intentos_fallidos: int = 0
    ultimo_intento_en: datetime | None = None
    bloqueado_hasta: datetime | None = None
    notificacion_enviada: bool = False


@dataclass(frozen=True)
class RegistroSeguridadLogin:
    id: int
    correo: str
    tipo_evento: TipoEventoSeguridadLogin
    fecha_hora: datetime
    ip_origen: str | None
    detalle: str
