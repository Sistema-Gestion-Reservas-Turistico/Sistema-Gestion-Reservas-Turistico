from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ActivarCuentaRequest:
    token: str = field(repr=False)


@dataclass(frozen=True)
class ReenviarActivacionRequest:
    correo: str


@dataclass(frozen=True)
class ActivarCuentaResponse:
    id: int
    correo: str
    estado: str
    fecha_activacion: datetime


@dataclass(frozen=True)
class ReenviarActivacionResponse:
    mensaje: str
    success: bool = True
