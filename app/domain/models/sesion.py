from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class SesionCreate:
    usuario_id: int
    correo: str
    rol: str
    token_hash: str = field(repr=False)
    inicio_en: datetime
    expira_en: datetime


@dataclass(frozen=True)
class MantenerSesionRequest:
    token: str = field(repr=False)


@dataclass(frozen=True)
class CerrarSesionRequest:
    token: str = field(repr=False)


@dataclass(frozen=True)
class SesionRenovadaResponse:
    token: str = field(repr=False)
    tipo: str
    expira_en: int
    inactividad_max: int


@dataclass(frozen=True)
class SesionActualResponse:
    usuario_id: int
    correo: str
    rol: str
    inicio_en: datetime
    ultima_actividad: datetime
    inactividad_max: int


@dataclass(frozen=True)
class CerrarSesionResponse:
    mensaje: str
    motivo_cierre: Literal["LOGOUT"]
    cerrada_en: datetime