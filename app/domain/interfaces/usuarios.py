from abc import ABC, abstractmethod

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
