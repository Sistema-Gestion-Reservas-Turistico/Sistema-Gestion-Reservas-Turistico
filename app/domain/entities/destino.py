from dataclasses import dataclass


@dataclass(frozen=True)
class Destino:
    id_destino: int
    nombre: str
    id_municipio: int
    latitud: float | None = None
    longitud: float | None = None
    estado_coordenadas: str = "PENDIENTES"