from dataclasses import dataclass


@dataclass(frozen=True)
class UbicacionItem:
    id: int
    nombre: str


@dataclass(frozen=True)
class ConsultaUbicacionesData:
    nivel: str
    id_padre: int | None
    total: int
    ubicaciones: list[UbicacionItem]


@dataclass(frozen=True)
class ConsultaUbicacionesResponse:
    mensaje: str
    data: ConsultaUbicacionesData
    success: bool


@dataclass(frozen=True)
class ErrorUbicacionesResponse:
    mensaje: str
    data: None = None
    success: bool = False