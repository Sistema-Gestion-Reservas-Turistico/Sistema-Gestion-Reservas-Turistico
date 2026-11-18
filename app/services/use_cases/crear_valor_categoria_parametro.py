from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class CrearValorCategoriaParametro:
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
        codigo: str,
        nombre: str,
        descripcion: str,
        orden: int | None,
        es_sistema: bool = False,
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
        return self._valores.crear(
            categoria.clave, codigo, nombre, descripcion, orden, es_sistema
        )
