from dataclasses import dataclass
from datetime import datetime, timezone

from app.domain.entities.destination import Destination, DestinationNotice
from app.domain.exceptions.destinations import (
    DestinationNotFoundError,
    DestinationPersistenceError,
    DuplicateDestinationError,
    InvalidNoticePeriodError,
    InvalidTourismTypeError,
    MunicipalityNotFoundError,
)
from app.domain.interfaces.destinations import DestinationRepository
from app.domain.interfaces.municipalities import MunicipalityRepository
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


TOURISM_TYPE_CATEGORY = "TIPO_TURISMO"
DESTINATION_STATUSES = {"ABIERTO", "RESTRINGIDO", "CERRADO"}


@dataclass(frozen=True)
class DestinationInput:
    name: str
    municipality_id: int
    tourism_types: tuple[str, ...]
    description: str | None = None
    activities: tuple[str, ...] = ()
    main_image_url: str | None = None
    destination_status: str = "ABIERTO"
    notices: tuple[DestinationNotice, ...] = ()


class SaveDestinationUseCase:
    def __init__(
        self,
        destinations: DestinationRepository,
        municipalities: MunicipalityRepository,
        tourism_parameters: ValoresCategoriaRepository,
    ) -> None:
        self._destinations = destinations
        self._municipalities = municipalities
        self._tourism_parameters = tourism_parameters

    def create(self, data: DestinationInput) -> Destination:
        return self._save(data, destination_id=None)

    def update(self, destination_id: int, data: DestinationInput) -> Destination:
        return self._save(data, destination_id=destination_id)

    def _save(
        self, data: DestinationInput, destination_id: int | None
    ) -> Destination:
        name = data.name.strip()
        if not name:
            raise ValueError("The destination name is required")
        if not data.tourism_types:
            raise ValueError("At least one tourism type must be provided")
        destination_status = data.destination_status.strip().upper()
        if destination_status not in DESTINATION_STATUSES:
            raise ValueError("The destination status is invalid")
        requested_codes = tuple(
            dict.fromkeys(
                code.strip().upper()
                for code in data.tourism_types
                if code.strip()
            )
        )
        if not requested_codes:
            raise ValueError("At least one tourism type must be provided")
        _validate_notice_periods(data.notices)

        try:
            current = (
                self._destinations.get_by_id(destination_id)
                if destination_id is not None
                else None
            )
            if destination_id is not None and current is None:
                raise DestinationNotFoundError()

            municipality = self._municipalities.get_by_id(data.municipality_id)
            if municipality is None or not municipality.enabled:
                raise MunicipalityNotFoundError()

            active_codes = {
                item.codigo.casefold(): item.codigo
                for item in self._tourism_parameters.list(
                    TOURISM_TYPE_CATEGORY, activo=True
                )
            }
            invalid_codes = [
                code for code in requested_codes if code.casefold() not in active_codes
            ]
            if invalid_codes:
                raise InvalidTourismTypeError(invalid_codes)
            duplicate = self._destinations.find_by_name_and_municipality(
                name, data.municipality_id
            )
            if duplicate is not None and duplicate.id != destination_id:
                raise DuplicateDestinationError()

            destination = Destination(
                id=current.id if current is not None else 0,
                name=name,
                description=data.description,
                municipality_id=data.municipality_id,
                tourism_types=tuple(active_codes[code.casefold()] for code in requested_codes),
                activities=tuple(
                    dict.fromkeys(
                        activity.strip()
                        for activity in data.activities
                        if activity.strip()
                    )
                ),
                main_image_url=data.main_image_url,
                destination_status=destination_status,
                coordinates_status=(
                    current.coordinates_status if current is not None else "PENDIENTES"
                ),
                status=current.status if current is not None else "ACTIVO",
                notices=data.notices,
            )
            if current is None:
                return self._destinations.create(destination)
            return self._destinations.update(destination)
        except (
            DestinationNotFoundError,
            DuplicateDestinationError,
            InvalidTourismTypeError,
            MunicipalityNotFoundError,
        ):
            raise
        except Exception as error:
            raise DestinationPersistenceError() from error


def _validate_notice_periods(notices: tuple[DestinationNotice, ...]) -> None:
    for notice in notices:
        if not notice.notice_type.strip() or not notice.message.strip():
            raise ValueError("Each notice requires a type and a message")
        if notice.valid_from is None or notice.valid_until is None:
            continue
        start = _as_utc(notice.valid_from)
        end = _as_utc(notice.valid_until)
        if end < start:
            raise InvalidNoticePeriodError()


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
