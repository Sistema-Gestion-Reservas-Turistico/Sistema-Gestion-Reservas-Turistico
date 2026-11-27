from dataclasses import dataclass, field


@dataclass(frozen=True)
class ActividadDestino:
    id: int
    nombre: str


@dataclass(frozen=True)
class Destino:
    id_destino: int
    nombre: str
    id_municipio: int
    latitud: float | None = None
    longitud: float | None = None
    estado_coordenadas: str = "PENDIENTES"
    descripcion: str = ""
    tipos_turismo: list[str] = field(default_factory=list)
    actividades: list[ActividadDestino] = field(default_factory=list)
    imagen_principal_url: str | None = None
    activo: bool = True