from dataclasses import dataclass


TIPO_HABITACION = "TIPO_HABITACION"
TIPO_ALIMENTACION = "TIPO_ALIMENTACION"
RESTRICCION_ALIMENTARIA = "RESTRICCION_ALIMENTARIA"


@dataclass(frozen=True)
class CategoriaAlojamientoAlimentacionCreate:
    clave: str
    nombre: str
    descripcion: str


@dataclass(frozen=True)
class ValorAlojamientoAlimentacionCreate:
    codigo: str
    nombre: str
    descripcion: str
    orden: int


@dataclass(frozen=True)
class ValorAlojamientoAlimentacionResponse:
    id: int
    codigo: str
    nombre: str
    orden: int
    activo: bool
    es_sistema: bool


@dataclass(frozen=True)
class CategoriaAlojamientoAlimentacionResponse:
    clave: str
    nombre: str
    valores: list[ValorAlojamientoAlimentacionResponse]


@dataclass(frozen=True)
class ParametrosAlojamientoAlimentacionResponse:
    categorias: list[CategoriaAlojamientoAlimentacionResponse]
