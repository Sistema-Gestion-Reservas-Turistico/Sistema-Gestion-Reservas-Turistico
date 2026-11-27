from dataclasses import dataclass


@dataclass(frozen=True)
class UbicacionDestinoData:
    municipio: str
    departamento: str
    pais: str


@dataclass(frozen=True)
class ActividadDestinoItem:
    id: int
    nombre: str


@dataclass(frozen=True)
class CoordenadasDestinoItem:
    latitud: float
    longitud: float


@dataclass(frozen=True)
class FichaDestinoData:
    id_destino: int
    nombre: str
    descripcion: str
    ubicacion: UbicacionDestinoData
    tipos_turismo: list[str]
    actividades: list[ActividadDestinoItem]
    coordenadas: CoordenadasDestinoItem | None
    imagen_principal_url: str | None


@dataclass(frozen=True)
class FichaDestinoResponse:
    mensaje: str
    data: FichaDestinoData
    success: bool


@dataclass(frozen=True)
class ErrorFichaDestinoResponse:
    mensaje: str
    data: None = None
    success: bool = False
