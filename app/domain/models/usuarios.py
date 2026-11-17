from dataclasses import dataclass
from dataclasses import dataclass, field


TIPO_DOCUMENTO = "TIPO_DOCUMENTO"
ROL_CLIENTE = "Cliente"
ESTADO_PENDIENTE_ACTIVACION = "PENDIENTE_ACTIVACION"


@dataclass(frozen=True)
class UsuarioRegistroCreate:
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    correo: str
    password: str = field(repr=False)
    acepta_tratamiento_datos: bool
    telefono: str | None = None


@dataclass(frozen=True)
class UsuarioRegistroResponse:
    id: int
    nombres: str
    apellidos: str
    correo: str
    estado: str


@dataclass(frozen=True)
class ErrorCampoItem:
    campo: str
    detalle: str

