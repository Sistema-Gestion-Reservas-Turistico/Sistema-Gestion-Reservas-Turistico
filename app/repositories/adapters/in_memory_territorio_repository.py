from threading import Lock

from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.entities.pais import Pais
from app.domain.interfaces.territorio import TerritorioRepository


class InMemoryTerritorioRepository(TerritorioRepository):
    def __init__(self) -> None:
        self._paises: dict[int, Pais] = {}
        self._departamentos: dict[int, Departamento] = {}
        self._municipios: dict[int, MunicipioTerritorial] = {}
        self._lock = Lock()

    def crear_pais_si_no_existe(self, pais: Pais) -> Pais:
        with self._lock:
            existente = self._paises.get(pais.id)
            if existente is not None:
                return existente
            self._paises[pais.id] = pais
            return pais

    def crear_departamento_si_no_existe(
        self, departamento: Departamento
    ) -> Departamento:
        with self._lock:
            existente = self._departamentos.get(departamento.id)
            if existente is not None:
                return existente
            self._departamentos[departamento.id] = departamento
            return departamento

    def crear_municipio_si_no_existe(
        self, municipio: MunicipioTerritorial
    ) -> MunicipioTerritorial:
        with self._lock:
            existente = self._municipios.get(municipio.id_municipio)
            if existente is not None:
                return existente
            self._municipios[municipio.id_municipio] = municipio
            return municipio

    def coordenadas_pertenecen_municipio(
        self,
        id_municipio: int,
        latitud: float,
        longitud: float,
    ) -> bool:
        with self._lock:
            municipio = self._municipios.get(id_municipio)
            return municipio is not None and (
                municipio.latitud_min <= latitud <= municipio.latitud_max
                and municipio.longitud_min <= longitud <= municipio.longitud_max
            )

    def listar_paises(self) -> list[Pais]:
        with self._lock:
            return list(self._paises.values())

    def listar_departamentos_por_pais(
        self, id_pais: int
    ) -> list[Departamento]:
        with self._lock:
            return [
                departamento
                for departamento in self._departamentos.values()
                if departamento.id_pais == id_pais
            ]

    def listar_municipios_por_departamento(
        self, id_departamento: int
    ) -> list[MunicipioTerritorial]:
        with self._lock:
            return [
                municipio
                for municipio in self._municipios.values()
                if municipio.id_departamento == id_departamento
                and municipio.habilitado
            ]