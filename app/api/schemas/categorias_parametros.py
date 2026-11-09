from pydantic import BaseModel, ConfigDict, Field


class CategoriaParametroCrear(BaseModel):
    """Campos requeridos para crear una categoría de parámetros."""

    clave: str = Field(min_length=1, max_length=50, pattern=r"^[A-Z0-9_]+$")
    nombre: str = Field(min_length=1, max_length=100)
    descripcion: str = ""


class CategoriaParametroEditar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion: str | None = None


class CategoriaParametroData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clave: str
    nombre: str
    descripcion: str


class CategoriaParametroResponse(BaseModel):
    mensaje: str
    data: CategoriaParametroData
    success: bool


class CategoriasParametroResponse(BaseModel):
    mensaje: str
    data: list[CategoriaParametroData]
    success: bool


class CategoriaParametroErrorResponse(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False
