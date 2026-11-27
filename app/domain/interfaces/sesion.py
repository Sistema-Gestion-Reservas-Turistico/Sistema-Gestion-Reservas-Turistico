from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.sesion import SesionUsuario
from app.domain.models.sesion import SesionCreate


class SesionRepository(ABC):
    @abstractmethod
    def crear(self, sesion: SesionCreate) -> SesionUsuario:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_token_hash(self, token_hash: str) -> SesionUsuario | None:
        raise NotImplementedError

    @abstractmethod
    def actualizar_actividad(
        self, token_hash: str, ultima_actividad: datetime
    ) -> SesionUsuario:
        raise NotImplementedError

    @abstractmethod
    def renovar_token(
        self,
        token_hash_actual: str,
        token_hash_nuevo: str,
        ultima_actividad: datetime,
        expira_en: datetime,
    ) -> SesionUsuario:
        raise NotImplementedError

    @abstractmethod
    def cerrar_por_inactividad(
        self, token_hash: str, cerrada_en: datetime
    ) -> SesionUsuario:
        raise NotImplementedError

    @abstractmethod
    def cerrar_por_logout(
        self, token_hash: str, cerrada_en: datetime
    ) -> SesionUsuario:
        raise NotImplementedError