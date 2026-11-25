from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from app.api.responses import ApiErrorResponse, ApiResponse, utc_timestamp


DataT = TypeVar("DataT")


class SesionApiResponse(ApiResponse[DataT], Generic[DataT]):
    timestamp: str = Field(default_factory=utc_timestamp)


class SesionApiErrorResponse(ApiErrorResponse):
    timestamp: str = Field(default_factory=utc_timestamp)


class SesionRenovadaData(BaseModel):
    token: str
    tipo: Literal["Bearer"]
    expira_en: int
    inactividad_max: int


class SesionRenovadaApiResponse(SesionApiResponse[SesionRenovadaData]):
    pass


class SesionActualData(BaseModel):
    usuario_id: int
    correo: str
    rol: str
    inicio_en: datetime
    ultima_actividad: datetime
    inactividad_max: int


class SesionActualApiResponse(SesionApiResponse[SesionActualData]):
    pass


class CerrarSesionData(BaseModel):
    mensaje: str
    motivo_cierre: Literal["LOGOUT"]
    cerrada_en: datetime


class CerrarSesionApiResponse(SesionApiResponse[CerrarSesionData]):
    pass


class SesionInactivaData(BaseModel):
    codigo: Literal["SESION_INACTIVA"]


class SesionInactivaErrorResponse(SesionApiErrorResponse):
    data: SesionInactivaData


class SesionErrorResponse(SesionApiErrorResponse):
    pass