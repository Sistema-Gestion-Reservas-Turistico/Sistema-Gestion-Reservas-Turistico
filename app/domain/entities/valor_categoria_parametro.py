from dataclasses import dataclass


@dataclass(frozen=True)
class ValorCategoriaParametro:
    id: int
    categoria: str
    codigo: str
    nombre: str
    descripcion: str
    orden: int
    activo: bool
