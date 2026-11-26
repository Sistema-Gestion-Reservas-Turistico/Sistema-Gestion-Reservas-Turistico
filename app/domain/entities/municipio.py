from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


_ZONA_HORARIA_COLOMBIA = timezone(timedelta(hours=-5))


def _fecha_actualizacion_inicial() -> datetime:
    return datetime.now(_ZONA_HORARIA_COLOMBIA)


@dataclass(frozen=True)
class MunicipioTerritorial:
    id_municipio: int
    latitud_min: float
    latitud_max: float
    longitud_min: float
    longitud_max: float
    nombre: str = ""
    id_departamento: int = 0
    habilitado: bool = True
    fecha_actualizacion: datetime = field(
        default_factory=_fecha_actualizacion_inicial
    )


Municipio = MunicipioTerritorial