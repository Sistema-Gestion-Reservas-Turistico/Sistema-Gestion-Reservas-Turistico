from pydantic import BaseModel, ConfigDict, Field


class ValorCategoriaCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(min_length=1)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""
    orden: int | None = Field(default=None, strict=True)


class ValorCategoriaEditar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = None
    orden: int | None = Field(default=None, strict=True)


class CambiarEstadoValorCategoria(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    activo: bool


class ValorCategoriaData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria: str
    codigo: str
    nombre: str
    descripcion: str
    orden: int
    activo: bool
    es_sistema: bool


class ValorCategoriaResponse(BaseModel):
    mensaje: str
    data: ValorCategoriaData
    success: bool


class ValorCategoriaEstadoData(BaseModel):
    id: int
    categoria: str
    codigo: str
    activo: bool


class ValorCategoriaEstadoResponse(BaseModel):
    mensaje: str
    data: ValorCategoriaEstadoData
    success: bool


class ValoresCategoriaResponse(BaseModel):
    mensaje: str
    data: list[ValorCategoriaData]
    success: bool


class ParametrosTransporteData(BaseModel):
    tipo_vehiculo: list[ValorCategoriaData]
    estado_vehiculo: list[ValorCategoriaData]


class ParametrosTransporteResponse(BaseModel):
    mensaje: str
    data: ParametrosTransporteData
    success: bool


class ValorCategoriaErrorResponse(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False
