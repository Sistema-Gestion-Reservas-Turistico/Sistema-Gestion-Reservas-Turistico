from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriaParametro:
    id: int
    clave: str
    nombre: str
    descripcion: str
