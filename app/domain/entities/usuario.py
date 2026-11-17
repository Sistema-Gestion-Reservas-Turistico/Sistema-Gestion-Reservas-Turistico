from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Usuario:
    id: int
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    correo: str
    telefono: str | None
    password_hash: str
    rol: str
    estado: str
    acepta_tratamiento_datos: bool
    fecha_aceptacion_datos: datetime
    intentos_fallidos: int
    bloqueado_hasta: datetime | None
    creado_en: datetime
