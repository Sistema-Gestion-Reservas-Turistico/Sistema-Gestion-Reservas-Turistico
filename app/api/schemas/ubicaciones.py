from pydantic import BaseModel


class UbicacionItemSchema(BaseModel):
    id: int
    nombre: str


class ConsultaUbicacionesDataSchema(BaseModel):
    nivel: str
    id_padre: int | None
    total: int
    ubicaciones: list[UbicacionItemSchema]


class ConsultaUbicacionesResponseSchema(BaseModel):
    mensaje: str
    data: ConsultaUbicacionesDataSchema
    success: bool


class ErrorUbicacionesResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False