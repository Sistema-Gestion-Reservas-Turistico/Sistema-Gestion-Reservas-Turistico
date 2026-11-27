from dataclasses import dataclass


@dataclass(frozen=True)
class Departamento:
    id: int
    id_pais: int
    nombre: str