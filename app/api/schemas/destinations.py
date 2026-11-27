from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.api.responses import ApiErrorResponse, ApiResponse


class DestinationNoticeInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    notice_type: str = Field(
        min_length=1,
        validation_alias=AliasChoices("notice_type", "tipo"),
    )
    message: str = Field(
        min_length=1,
        validation_alias=AliasChoices("message", "mensaje"),
    )
    valid_from: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("valid_from", "vigente_desde"),
    )
    valid_until: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("valid_until", "vigente_hasta"),
    )


class DestinationInput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(
        min_length=1,
        max_length=160,
        validation_alias=AliasChoices("name", "nombre"),
    )
    municipality_id: int = Field(
        gt=0,
        validation_alias=AliasChoices("municipality_id", "id_municipio"),
    )
    tourism_types: list[str] = Field(
        min_length=1,
        validation_alias=AliasChoices("tourism_types", "tipos_turismo"),
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        validation_alias=AliasChoices("description", "descripcion"),
    )
    activities: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("activities", "actividades"),
    )
    main_image_url: str | None = Field(
        default=None,
        max_length=2048,
        validation_alias=AliasChoices("main_image_url", "imagen_principal_url"),
    )
    destination_status: Literal["ABIERTO", "RESTRINGIDO", "CERRADO"] = Field(
        default="ABIERTO",
        validation_alias=AliasChoices("destination_status", "estado_destino"),
    )
    notices: list[DestinationNoticeInput] = Field(
        default_factory=list,
        validation_alias=AliasChoices("notices", "avisos"),
    )


class DestinationData(BaseModel):
    destination_id: int
    name: str
    municipality_id: int
    tourism_types: list[str]
    destination_status: str
    coordinates_status: str
    status: str


class DestinationResponse(ApiResponse[DestinationData]):
    pass


class DestinationErrorResponse(ApiErrorResponse):
    pass
