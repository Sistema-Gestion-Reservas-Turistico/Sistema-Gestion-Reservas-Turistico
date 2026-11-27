from dataclasses import dataclass


@dataclass(frozen=True)
class Pais:
    id: int
    nombre: str