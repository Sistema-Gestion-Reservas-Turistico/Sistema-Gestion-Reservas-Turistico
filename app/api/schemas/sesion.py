from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from app.api.responses import ApiErrorResponse, ApiResponse, utc_timestamp
from app.api.schemas.autenticacion import UsuarioAutenticadoData


DataT = TypeVar("DataT")


class SesionApiResponse(ApiResponse[DataT], Generic[DataT]):
    timestamp: str = Field(default_factory=utc_timestamp)


class SesionApiErrorResponse(ApiErrorResponse):
    timestamp: str = Field(default_factory=utc_timestamp)


class SesionRenovadaData(BaseModel):
    token: str
    token_type: Literal["Bearer"]
    expires_in: int
    inactivity_timeout: int


class SesionRenovadaApiResponse(SesionApiResponse[SesionRenovadaData]):
    pass


class SesionActualData(BaseModel):
    user_id: int
    email: str
    role: str
    started_at: datetime
    last_activity: datetime
    inactivity_timeout: int
    user: UsuarioAutenticadoData | None = None


class SesionActualApiResponse(SesionApiResponse[SesionActualData]):
    pass


class CerrarSesionData(BaseModel):
    message: str
    close_reason: Literal["LOGOUT"]
    closed_at: datetime


class CerrarSesionApiResponse(SesionApiResponse[CerrarSesionData]):
    pass


class SesionInactivaData(BaseModel):
    code: Literal["SESION_INACTIVA"]


class SesionInactivaErrorResponse(SesionApiErrorResponse):
    data: SesionInactivaData


class SesionErrorResponse(SesionApiErrorResponse):
    pass
