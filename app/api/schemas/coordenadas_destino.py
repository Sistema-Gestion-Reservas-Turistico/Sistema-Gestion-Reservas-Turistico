from typing import Literal

from pydantic import BaseModel, Field


class RegistrarCoordenadasRequest(BaseModel):
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)


class CoordenadasDestinoResponseData(BaseModel):
    id_destino: int
    nombre: str
    id_municipio: int
    latitud: float
    longitud: float
    estado_coordenadas: str


class RegistrarCoordenadasResponse(BaseModel):
    mensaje: str
    data: CoordenadasDestinoResponseData
    success: Literal[True] = True


class ErrorCoordenadasResponse(BaseModel):
    mensaje: str
    data: None = None
    success: Literal[False] = False