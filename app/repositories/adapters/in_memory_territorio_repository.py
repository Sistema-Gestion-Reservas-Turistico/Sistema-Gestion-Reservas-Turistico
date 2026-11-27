from dataclasses import replace
from datetime import datetime
from threading import Lock

from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.entities.pais import Pais
from app.domain.entities.sugerencia_territorial import SugerenciaTerritorial
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

    def consultar_estructura_territorial(
        self, id_pais: int, id_departamento: int | None = None
    ) -> tuple[
        Pais | None,
        list[tuple[Departamento, list[MunicipioTerritorial]]],
    ]:
        with self._lock:
            pais = self._paises.get(id_pais)
            if pais is None:
                return None, []

            departamentos = [
                departamento
                for departamento in self._departamentos.values()
                if departamento.id_pais == id_pais
                and (
                    id_departamento is None
                    or departamento.id == id_departamento
                )
            ]
            departamentos.sort(key=lambda item: item.nombre.casefold())

            estructura = []
            for departamento in departamentos:
                municipios = [
                    municipio
                    for municipio in self._municipios.values()
                    if municipio.id_departamento == departamento.id
                ]
                municipios.sort(key=lambda item: item.nombre.casefold())
                estructura.append((departamento, municipios))

            return pais, estructura

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

    def listar_ubicaciones_autocompletar(self) -> list[SugerenciaTerritorial]:
        with self._lock:
            sugerencias = [
                SugerenciaTerritorial(
                    id=departamento.id,
                    nombre=departamento.nombre,
                    tipo="DEPARTAMENTO",
                )
                for departamento in self._departamentos.values()
            ]
            sugerencias.extend(
                SugerenciaTerritorial(
                    id=municipio.id_municipio,
                    nombre=municipio.nombre,
                    tipo="MUNICIPIO",
                    departamento=self._departamentos[
                        municipio.id_departamento
                    ].nombre,
                )
                for municipio in self._municipios.values()
                if municipio.habilitado
                and municipio.id_departamento in self._departamentos
            )
            return sugerencias

    def obtener_municipio(
        self, id_municipio: int
    ) -> MunicipioTerritorial | None:
        with self._lock:
            return self._municipios.get(id_municipio)

    def obtener_jerarquia_municipio(
        self, id_municipio: int
    ) -> tuple[MunicipioTerritorial, Departamento, Pais] | None:
        with self._lock:
            municipio = self._municipios.get(id_municipio)
            if municipio is None:
                return None
            departamento = self._departamentos.get(municipio.id_departamento)
            if departamento is None:
                return None
            pais = self._paises.get(departamento.id_pais)
            if pais is None:
                return None
            return municipio, departamento, pais

    def actualizar_disponibilidad_municipio(
        self,
        id_municipio: int,
        habilitado: bool,
        fecha_actualizacion: datetime,
    ) -> MunicipioTerritorial | None:
        with self._lock:
            municipio = self._municipios.get(id_municipio)
            if municipio is None:
                return None
            actualizado = replace(
                municipio,
                habilitado=habilitado,
                fecha_actualizacion=fecha_actualizacion,
            )
            self._municipios[id_municipio] = actualizado
            return actualizado