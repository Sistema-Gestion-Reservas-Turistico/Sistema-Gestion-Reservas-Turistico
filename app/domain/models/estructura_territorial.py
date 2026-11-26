from dataclasses import dataclass


@dataclass(frozen=True)
class MunicipioEstructuraItem:
    id: int
    nombre: str
    habilitado: bool


@dataclass(frozen=True)
class DepartamentoEstructuraItem:
    id: int
    nombre: str
    municipios: list[MunicipioEstructuraItem]


@dataclass(frozen=True)
class EstructuraTerritorialData:
    id_pais: int
    total_departamentos: int
    total_municipios: int
    departamentos: list[DepartamentoEstructuraItem]
    nombre: str | None = None


@dataclass(frozen=True)
class EstructuraTerritorialResponse:
    mensaje: str
    data: EstructuraTerritorialData
    success: bool


@dataclass(frozen=True)
class ErrorEstructuraTerritorialResponse:
    mensaje: str
    data: None = None
    success: bool = False
