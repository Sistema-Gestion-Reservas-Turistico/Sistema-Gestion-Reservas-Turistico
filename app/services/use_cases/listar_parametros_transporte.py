from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


TIPO_VEHICULO = "TIPO_VEHICULO"
ESTADO_VEHICULO = "ESTADO_VEHICULO"


class ListarParametrosTransporte:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> dict[str, list[ValorCategoriaParametro]]:
        categorias = {
            categoria.clave.casefold(): categoria
            for categoria in self._categorias.listar()
        }
        resultado: dict[str, list[ValorCategoriaParametro]] = {}
        for clave in (TIPO_VEHICULO, ESTADO_VEHICULO):
            categoria = categorias.get(clave.casefold())
            if categoria is None:
                raise CategoriaValorNoEncontradaError(clave)
            resultado[clave.casefold()] = self._valores.listar(categoria.clave)
        return resultado