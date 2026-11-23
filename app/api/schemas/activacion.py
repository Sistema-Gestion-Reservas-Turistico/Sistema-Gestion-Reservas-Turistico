from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.responses import ApiErrorResponse, ApiResponse

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


class ActivarCuentaResponseSchema(ApiResponse[ActivarCuentaData]):
    pass


class ReenviarActivacionResponseSchema(ApiResponse[None]):
    pass


class ActivacionErrorResponse(ApiErrorResponse):
    pass
