from dataclasses import dataclass


@dataclass(frozen=True)
class ActualizarDisponibilidadMunicipioCreate:
    habilitado: bool


@dataclass(frozen=True)
class DisponibilidadMunicipioData:
    id_municipio: int
    nombre: str
    id_departamento: int
    habilitado: bool
    fecha_actualizacion: str


@dataclass(frozen=True)
class DisponibilidadMunicipioResponse:
    mensaje: str
    data: DisponibilidadMunicipioData
    success: bool = True


@dataclass(frozen=True)
class ErrorDisponibilidadMunicipioResponse:
    mensaje: str
    data: None = None
    success: bool = False