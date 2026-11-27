from app.domain.entities.municipality import Municipality
from app.domain.interfaces.municipalities import MunicipalityRepository


class InMemoryMunicipalityRepository(MunicipalityRepository):
    """Temporary local catalog until the HU-14 municipality adapter is available."""

    def __init__(self) -> None:
        self._municipalities = {
            63690: Municipality(id=63690, name="Salento", enabled=True),
        }

    def get_by_id(self, municipality_id: int) -> Municipality | None:
        return self._municipalities.get(municipality_id)
