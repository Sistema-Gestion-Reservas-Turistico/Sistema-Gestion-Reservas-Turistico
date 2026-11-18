from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.usuario import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def registrar(self, usuario: Usuario) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_correo(self, correo: str) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def activar(
        self, usuario_id: int, fecha_activacion: datetime
    ) -> Usuario | None:
        raise NotImplementedError
