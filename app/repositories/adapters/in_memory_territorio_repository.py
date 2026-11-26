from threading import Lock

from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.interfaces.territorio import TerritorioRepository


class InMemoryTerritorioRepository(TerritorioRepository):
    def __init__(self) -> None:
        self._municipios: dict[int, MunicipioTerritorial] = {}
        self._lock = Lock()

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