from pydantic import BaseModel, ConfigDict


class ActualizarDisponibilidadMunicipioRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    habilitado: bool


class DisponibilidadMunicipioDataSchema(BaseModel):
    id_municipio: int
    nombre: str
    id_departamento: int
    habilitado: bool
    fecha_actualizacion: str


class DisponibilidadMunicipioResponseSchema(BaseModel):
    mensaje: str
    data: DisponibilidadMunicipioDataSchema
    success: bool


class ErrorDisponibilidadMunicipioResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False