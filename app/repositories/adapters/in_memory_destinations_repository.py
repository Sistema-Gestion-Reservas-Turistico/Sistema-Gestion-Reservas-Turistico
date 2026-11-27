from threading import RLock

from app.domain.entities.destination import Destination
from app.domain.exceptions.destinations import (
    DestinationNotFoundError,
    DuplicateDestinationError,
)
from app.domain.interfaces.destinations import DestinationRepository


class InMemoryDestinationRepository(DestinationRepository):
    def __init__(self) -> None:
        self._destinations: dict[int, Destination] = {}
        self._next_id = 1
        self._lock = RLock()

    def create(self, destination: Destination) -> Destination:
        with self._lock:
            if any(
                existing.municipality_id == destination.municipality_id
                and existing.name.casefold() == destination.name.casefold()
                for existing in self._destinations.values()
            ):
                raise DuplicateDestinationError()
            saved = Destination(
                id=self._next_id,
                name=destination.name,
                description=destination.description,
                municipality_id=destination.municipality_id,
                tourism_types=destination.tourism_types,
                activities=destination.activities,
                main_image_url=destination.main_image_url,
                destination_status=destination.destination_status,
                coordinates_status=destination.coordinates_status,
                status=destination.status,
                notices=destination.notices,
            )
            self._destinations[saved.id] = saved
            self._next_id += 1
            return saved

    def get_by_id(self, destination_id: int) -> Destination | None:
        with self._lock:
            return self._destinations.get(destination_id)

    def find_by_name_and_municipality(
        self, name: str, municipality_id: int
    ) -> Destination | None:
        normalized_name = name.strip().casefold()
        with self._lock:
            return next(
                (
                    destination
                    for destination in self._destinations.values()
                    if destination.municipality_id == municipality_id
                    and destination.name.casefold() == normalized_name
                ),
                None,
            )

    def update(self, destination: Destination) -> Destination:
        with self._lock:
            if any(
                existing.id != destination.id
                and existing.municipality_id == destination.municipality_id
                and existing.name.casefold() == destination.name.casefold()
                for existing in self._destinations.values()
            ):
                raise DuplicateDestinationError()
            if destination.id not in self._destinations:
                raise DestinationNotFoundError()
            self._destinations[destination.id] = destination
            return destination
