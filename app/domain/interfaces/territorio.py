from abc import ABC, abstractmethod

from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.entities.pais import Pais


class TerritorioRepository(ABC):
    @abstractmethod
    def crear_pais_si_no_existe(self, pais: Pais) -> Pais:
        raise NotImplementedError

    @abstractmethod
    def crear_departamento_si_no_existe(
        self, departamento: Departamento
    ) -> Departamento:
        raise NotImplementedError

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

    @abstractmethod
    def listar_paises(self) -> list[Pais]:
        raise NotImplementedError

    @abstractmethod
    def listar_departamentos_por_pais(
        self, id_pais: int
    ) -> list[Departamento]:
        raise NotImplementedError

    @abstractmethod
    def listar_municipios_por_departamento(
        self, id_departamento: int
    ) -> list[MunicipioTerritorial]:
        raise NotImplementedError