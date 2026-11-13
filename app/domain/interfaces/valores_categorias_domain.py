from abc import ABC, abstractmethod

from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro


class ValoresCategoriaRepository(ABC):
    @abstractmethod
    def listar(
        self, categoria: str, activo: bool | None = None
    ) -> list[ValorCategoriaParametro]:
        raise NotImplementedError

    @abstractmethod
    def crear(
        self,
        categoria: str,
        codigo: str,
        nombre: str,
        descripcion: str,
        orden: int | None,
    ) -> ValorCategoriaParametro:
        raise NotImplementedError

    @abstractmethod
    def actualizar(
        self,
        categoria: str,
        valor_id: int,
        nombre: str | None,
        descripcion: str | None,
        orden: int | None,
    ) -> ValorCategoriaParametro:
        raise NotImplementedError

    @abstractmethod
    def actualizar_estado(
        self, categoria: str, valor_id: int, activo: bool
    ) -> ValorCategoriaParametro:
        raise NotImplementedError
