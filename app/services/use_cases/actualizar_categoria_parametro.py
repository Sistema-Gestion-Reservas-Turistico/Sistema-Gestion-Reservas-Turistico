from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)


class ActualizarCategoriaParametro:
    def __init__(self, repositorio: CategoriaParametroRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self,
        categoria_id: int,
        nombre: str | None,
        descripcion: str | None,
    ) -> CategoriaParametro:
        if self._repositorio.obtener_por_id(categoria_id) is None:
            raise CategoriaParametroNoEncontradaError(categoria_id)
        return self._repositorio.actualizar(categoria_id, nombre, descripcion)
