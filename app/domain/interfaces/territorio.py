from abc import ABC, abstractmethod

from app.domain.entities.municipio import MunicipioTerritorial


class TerritorioRepository(ABC):
    @abstractmethod
    def crear_municipio_si_no_existe(
        self, municipio: MunicipioTerritorial
    ) -> MunicipioTerritorial:
        raise NotImplementedError

    @abstractmethod
    def coordenadas_pertenecen_municipio(
        self,
        id_municipio: int,
        latitud: float,
        longitud: float,
    ) -> bool:
        raise NotImplementedError