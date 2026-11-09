from abc import ABC, abstractmethod

from app.domain.entities.categoria_parametro import CategoriaParametro


class CategoriaParametroRepository(ABC):
    @abstractmethod
    def crear(self, categoria: CategoriaParametro) -> CategoriaParametro:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[CategoriaParametro]:
        raise NotImplementedError

    @abstractmethod
    def obtener_por_id(self, categoria_id: int) -> CategoriaParametro | None:
        raise NotImplementedError

    @abstractmethod
    def actualizar(
        self, categoria_id: int, nombre: str | None, descripcion: str | None
    ) -> CategoriaParametro:
        raise NotImplementedError
