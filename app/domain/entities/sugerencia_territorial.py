from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SugerenciaTerritorial:
    id: int
    nombre: str
    tipo: Literal["DEPARTAMENTO", "MUNICIPIO"]
    departamento: str | None = None