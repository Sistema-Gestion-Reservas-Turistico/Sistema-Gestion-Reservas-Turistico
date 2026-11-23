from pydantic import BaseModel, ConfigDict, Field

from app.api.responses import ApiErrorResponse, ApiResponse


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


class ValorCategoriaResponse(ApiResponse[ValorCategoriaData]):
    pass


class ValorCategoriaEstadoData(BaseModel):
    id: int
    categoria: str
    codigo: str
    activo: bool


class ValorCategoriaEstadoResponse(ApiResponse[ValorCategoriaEstadoData]):
    pass


class ValoresCategoriaResponse(ApiResponse[list[ValorCategoriaData]]):
    pass


class ParametrosTransporteData(BaseModel):
    tipo_vehiculo: list[ValorCategoriaData]
    estado_vehiculo: list[ValorCategoriaData]


class ParametrosTransporteResponse(ApiResponse[ParametrosTransporteData]):
    pass


class ValorCategoriaErrorResponse(ApiErrorResponse):
    pass


class ValorParametroPagoData(BaseModel):
    id: int
    codigo: str
    nombre: str
    orden: int
    activo: bool
    es_sistema: bool


class CategoriaParametroPagoData(BaseModel):
    clave: str
    nombre: str
    valores: list[ValorParametroPagoData]


class ParametrosPagoData(BaseModel):
    categorias: list[CategoriaParametroPagoData]


class ParametrosPagoResponse(ApiResponse[ParametrosPagoData]):
    pass


class ParametrosPagoErrorResponse(ApiErrorResponse):
    pass


class ParametroVigenteData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categoria: str
    codigo: str
    nombre: str
    descripcion: str
    orden: int


class ParametroCategoriaItemData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    descripcion: str
    orden: int


class ParametrosVigentesCategoriaData(BaseModel):
    categoria: str
    valores: list[ParametroCategoriaItemData]


class ParametroVigenteResponse(ApiResponse[ParametroVigenteData]):
    pass


class ParametrosVigentesCategoriaResponse(ApiResponse[ParametrosVigentesCategoriaData]):
    pass


class ValorAlojamientoAlimentacionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    codigo: str = Field(min_length=1)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""
    orden: int | None = Field(default=None, strict=True)


class CategoriaAlojamientoAlimentacionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clave: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""


class ValorAlojamientoAlimentacionData(BaseModel):
    id: int
    codigo: str
    nombre: str
    orden: int
    activo: bool
    es_sistema: bool


class CategoriaAlojamientoAlimentacionData(BaseModel):
    clave: str
    nombre: str
    valores: list[ValorAlojamientoAlimentacionData]


class ParametrosAlojamientoAlimentacionData(BaseModel):
    categorias: list[CategoriaAlojamientoAlimentacionData]


class ParametrosAlojamientoAlimentacionResponse(
    ApiResponse[ParametrosAlojamientoAlimentacionData]
):
    pass


class ParametrosAlojamientoAlimentacionErrorResponse(ApiErrorResponse):
    pass
