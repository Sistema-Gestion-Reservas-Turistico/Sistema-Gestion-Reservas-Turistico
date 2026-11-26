from dataclasses import replace
from threading import Lock

from app.domain.entities.destino import Destino
from app.domain.exceptions.destino import DestinoNoEncontradoError
from app.domain.interfaces.destino import DestinoRepository


class InMemoryDestinoRepository(DestinoRepository):
    def __init__(self) -> None:
        self._destinos: dict[int, Destino] = {}
        self._lock = Lock()

    def obtener_por_id(self, id_destino: int) -> Destino | None:
        with self._lock:
            return self._destinos.get(id_destino)

    def actualizar_coordenadas(
        self,
        id_destino: int,
        latitud: float,
        longitud: float,
    ) -> Destino:
        with self._lock:
            destino = self._destinos.get(id_destino)
            if destino is None:
                raise DestinoNoEncontradoError()
            actualizado = replace(
                destino,
                latitud=latitud,
                longitud=longitud,
                estado_coordenadas="REGISTRADAS",
            )
            self._destinos[id_destino] = actualizado
            return actualizado

    def crear_si_no_existe(self, destino: Destino) -> Destino:
        with self._lock:
            existente = self._destinos.get(destino.id_destino)
            if existente is not None:
                return existente
            self._destinos[destino.id_destino] = destino
            return destino