from typing import Literal

from pydantic import BaseModel


class SugerenciaUbicacionItemSchema(BaseModel):
    id: int
    nombre: str
    tipo: Literal["DEPARTAMENTO", "MUNICIPIO"]
    departamento: str | None = None


class AutocompletarUbicacionesDataSchema(BaseModel):
    consulta: str
    total: int
    sugerencias: list[SugerenciaUbicacionItemSchema]


class AutocompletarUbicacionesResponseSchema(BaseModel):
    mensaje: str
    data: AutocompletarUbicacionesDataSchema
    success: bool


class ErrorAutocompletarResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False