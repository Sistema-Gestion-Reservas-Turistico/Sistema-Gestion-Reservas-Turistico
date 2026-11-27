from abc import ABC, abstractmethod

from app.domain.entities.municipality import Municipality


class MunicipalityRepository(ABC):
    @abstractmethod
    def get_by_id(self, municipality_id: int) -> Municipality | None:
        raise NotImplementedError
