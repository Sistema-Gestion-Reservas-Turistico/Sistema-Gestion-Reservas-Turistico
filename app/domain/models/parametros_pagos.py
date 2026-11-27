from dataclasses import dataclass


METODO_PAGO = "METODO_PAGO"
ESTADO_TRANSACCION = "ESTADO_TRANSACCION"


@dataclass(frozen=True)
class CategoriaParametroPagoCreate:
    clave: str
    nombre: str
    descripcion: str


@dataclass(frozen=True)
class ValorParametroPagoCreate:
    codigo: str
    nombre: str
    descripcion: str
    orden: int
    es_sistema: bool


@dataclass(frozen=True)
class ValorParametroPagoResponse:
    id: int
    codigo: str
    nombre: str
    orden: int
    activo: bool
    es_sistema: bool


@dataclass(frozen=True)
class CategoriaParametroPagoResponse:
    clave: str
    nombre: str
    valores: list[ValorParametroPagoResponse]


@dataclass(frozen=True)
class ParametrosPagoResponse:
    categorias: list[CategoriaParametroPagoResponse]
