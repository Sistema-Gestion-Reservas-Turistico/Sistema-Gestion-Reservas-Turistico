from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenActivacionCuenta:
    id: int
    usuario_id: int
    correo_normalizado: str
    token_hash: str
    creado_en: datetime
    expira_en: datetime
    usado: bool = False
    usado_en: datetime | None = None
    invalidado: bool = False
