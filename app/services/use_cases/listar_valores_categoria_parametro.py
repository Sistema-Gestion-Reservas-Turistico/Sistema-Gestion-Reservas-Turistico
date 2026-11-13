from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class ListarValoresCategoriaParametro:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(
        self, clave: str, activo: bool | None = None
    ) -> list[ValorCategoriaParametro]:
        if not any(
            categoria.clave.casefold() == clave.casefold()
            for categoria in self._categorias.listar()
        ):
            raise CategoriaValorNoEncontradaError(clave)
        return self._valores.listar(clave, activo)
