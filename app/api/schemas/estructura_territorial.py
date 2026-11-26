from pydantic import BaseModel


class MunicipioEstructuraItemSchema(BaseModel):
    id: int
    nombre: str
    habilitado: bool


class DepartamentoEstructuraItemSchema(BaseModel):
    id: int
    nombre: str
    municipios: list[MunicipioEstructuraItemSchema]


class EstructuraTerritorialDataSchema(BaseModel):
    id_pais: int
    nombre: str | None = None
    total_departamentos: int
    total_municipios: int
    departamentos: list[DepartamentoEstructuraItemSchema]


class EstructuraTerritorialResponseSchema(BaseModel):
    mensaje: str
    data: EstructuraTerritorialDataSchema
    success: bool


class ErrorEstructuraTerritorialResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False
