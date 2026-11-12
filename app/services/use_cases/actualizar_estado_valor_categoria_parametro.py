from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class ActualizarEstadoValorCategoriaParametro:
    def __init__(self, repositorio: ValoresCategoriaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self, categoria: str, valor_id: int, activo: bool
    ) -> ValorCategoriaParametro:
        return self._repositorio.actualizar_estado(categoria, valor_id, activo)
