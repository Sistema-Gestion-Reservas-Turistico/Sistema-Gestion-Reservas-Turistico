from dataclasses import dataclass


@dataclass(frozen=True)
class MunicipioTerritorial:
    id_municipio: int
    latitud_min: float
    latitud_max: float
    longitud_min: float
    longitud_max: float