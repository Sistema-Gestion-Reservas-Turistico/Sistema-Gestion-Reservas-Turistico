from pydantic import BaseModel


class UbicacionDestinoDataSchema(BaseModel):
    municipio: str
    departamento: str
    pais: str


class ActividadDestinoItemSchema(BaseModel):
    id: int
    nombre: str


class CoordenadasDestinoItemSchema(BaseModel):
    latitud: float
    longitud: float


class FichaDestinoDataSchema(BaseModel):
    id_destino: int
    nombre: str
    descripcion: str
    ubicacion: UbicacionDestinoDataSchema
    tipos_turismo: list[str]
    actividades: list[ActividadDestinoItemSchema]
    coordenadas: CoordenadasDestinoItemSchema | None
    imagen_principal_url: str | None


class FichaDestinoResponseSchema(BaseModel):
    mensaje: str
    data: FichaDestinoDataSchema
    success: bool


class ErrorFichaDestinoResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False
