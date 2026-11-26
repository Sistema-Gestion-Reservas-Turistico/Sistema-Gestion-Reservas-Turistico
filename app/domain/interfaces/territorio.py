from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.entities.pais import Pais
from app.domain.entities.sugerencia_territorial import SugerenciaTerritorial


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
    def consultar_estructura_territorial(
        self, id_pais: int, id_departamento: int | None = None
    ) -> tuple[
        Pais | None,
        list[tuple[Departamento, list[MunicipioTerritorial]]],
    ]:
        raise NotImplementedError

    @abstractmethod
    def listar_municipios_por_departamento(
        self, id_departamento: int
    ) -> list[MunicipioTerritorial]:
        raise NotImplementedError

    @abstractmethod
    def listar_ubicaciones_autocompletar(self) -> list[SugerenciaTerritorial]:
        raise NotImplementedError

    @abstractmethod
    def obtener_municipio(
        self, id_municipio: int
    ) -> MunicipioTerritorial | None:
        raise NotImplementedError

    @abstractmethod
    def obtener_jerarquia_municipio(
        self, id_municipio: int
    ) -> tuple[MunicipioTerritorial, Departamento, Pais] | None:
        raise NotImplementedError

    @abstractmethod
    def actualizar_disponibilidad_municipio(
        self,
        id_municipio: int,
        habilitado: bool,
        fecha_actualizacion: datetime,
    ) -> MunicipioTerritorial | None:
        raise NotImplementedError