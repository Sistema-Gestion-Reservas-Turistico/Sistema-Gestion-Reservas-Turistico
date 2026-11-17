from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.models.activacion import ActivarCuentaRequest


class ActivarCuentaRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: str = Field(strict=True, min_length=1, repr=False)

    def to_domain(self) -> ActivarCuentaRequest:
        return ActivarCuentaRequest(token=self.token)


class ReenviarActivacionRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    correo: EmailStr


class ActivarCuentaData(BaseModel):
    id: int
    correo: str
    estado: str


class ActivarCuentaResponseSchema(BaseModel):
    mensaje: str
    data: ActivarCuentaData
    success: bool


class ReenviarActivacionResponseSchema(BaseModel):
    mensaje: str
    data: None = None
    success: bool = True


class ActivacionErrorResponse(BaseModel):
    mensaje: str
    data: None = None
    success: bool = False
