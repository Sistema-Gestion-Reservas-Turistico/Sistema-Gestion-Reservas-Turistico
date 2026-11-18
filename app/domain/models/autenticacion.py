from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class LoginRequest:
    correo: str
    password: str = field(repr=False)


@dataclass(frozen=True)
class LoginExitosoResponse:
    id: int
    nombres: str
    apellidos: str
    correo: str
    rol: str


@dataclass(frozen=True)
class LoginErrorCredencialesResponse:
    intentos_restantes: int


@dataclass(frozen=True)
class LoginBloqueadoResponse:
    bloqueada_hasta: datetime
    minutos_restantes: int
