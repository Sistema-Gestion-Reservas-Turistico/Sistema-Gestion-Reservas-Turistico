from abc import ABC, abstractmethod

from app.domain.entities.destination import Destination


class DestinationRepository(ABC):
    @abstractmethod
    def create(self, destination: Destination) -> Destination:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, destination_id: int) -> Destination | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_name_and_municipality(
        self, name: str, municipality_id: int
    ) -> Destination | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, destination: Destination) -> Destination:
        raise NotImplementedError
