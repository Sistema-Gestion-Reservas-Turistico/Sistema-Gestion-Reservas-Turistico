from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)


class CrearCategoriaParametro:
    def __init__(self, repositorio: CategoriaParametroRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(self, clave: str, nombre: str, descripcion: str) -> CategoriaParametro:
        categoria = CategoriaParametro(
            id=0,
            clave=clave,
            nombre=nombre,
            descripcion=descripcion,
        )
        return self._repositorio.crear(categoria)
