from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SugerenciaUbicacionItem:
    id: int
    nombre: str
    tipo: Literal["DEPARTAMENTO", "MUNICIPIO"]
    departamento: str | None = None


@dataclass(frozen=True)
class AutocompletarUbicacionesData:
    consulta: str
    total: int
    sugerencias: list[SugerenciaUbicacionItem]


@dataclass(frozen=True)
class AutocompletarUbicacionesResponse:
    mensaje: str
    data: AutocompletarUbicacionesData
    success: bool


@dataclass(frozen=True)
class ErrorAutocompletarResponse:
    mensaje: str
    data: None = None
    success: bool = False