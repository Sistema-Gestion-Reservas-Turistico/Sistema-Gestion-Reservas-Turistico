from dataclasses import dataclass


@dataclass(frozen=True)
class Municipality:
    id: int
    name: str
    enabled: bool = True
