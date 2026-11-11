from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class ActualizarValorCategoriaParametro:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(
        self,
        clave: str,
        valor_id: int,
        nombre: str | None,
        descripcion: str | None,
        orden: int | None,
    ) -> ValorCategoriaParametro:
        categoria = next(
            (
                item
                for item in self._categorias.listar()
                if item.clave.casefold() == clave.casefold()
            ),
            None,
        )
        if categoria is None:
            raise CategoriaValorNoEncontradaError(clave)
        return self._valores.actualizar(
            categoria.clave, valor_id, nombre, descripcion, orden
        )
