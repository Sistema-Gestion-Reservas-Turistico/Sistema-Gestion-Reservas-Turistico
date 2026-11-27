from abc import ABC, abstractmethod

from app.domain.entities.destino import Destino


class DestinoRepository(ABC):
    @abstractmethod
    def obtener_por_id(self, id_destino: int) -> Destino | None:
        raise NotImplementedError

    @abstractmethod
    def actualizar_coordenadas(
        self,
        id_destino: int,
        latitud: float,
        longitud: float,
    ) -> Destino:
        raise NotImplementedError

    @abstractmethod
    def crear_si_no_existe(self, destino: Destino) -> Destino:
        raise NotImplementedError