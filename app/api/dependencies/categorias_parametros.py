from functools import lru_cache

from app.repositories.adapters.in_memory_categorias_parametros_repository import (
    InMemoryCategoriaParametroRepository,
)
from app.services.use_cases.actualizar_categoria_parametro import (
    ActualizarCategoriaParametro,
)
from app.services.use_cases.crear_categoria_parametro import CrearCategoriaParametro


@lru_cache
def obtener_repositorio_categoria_parametro() -> InMemoryCategoriaParametroRepository:
    return InMemoryCategoriaParametroRepository()


def obtener_caso_crear_categoria_parametro() -> CrearCategoriaParametro:
    return CrearCategoriaParametro(obtener_repositorio_categoria_parametro())


def obtener_caso_actualizar_categoria_parametro() -> ActualizarCategoriaParametro:
    return ActualizarCategoriaParametro(obtener_repositorio_categoria_parametro())
