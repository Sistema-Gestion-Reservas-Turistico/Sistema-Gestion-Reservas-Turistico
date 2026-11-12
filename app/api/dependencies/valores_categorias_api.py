from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.repositories.adapters.in_memory_valores_categorias_repository import (
    InMemoryValoresCategoriaRepository,
)
from app.services.use_cases.actualizar_valor_categoria_parametro import (
    ActualizarValorCategoriaParametro,
)
from app.services.use_cases.actualizar_estado_valor_categoria_parametro import (
    ActualizarEstadoValorCategoriaParametro,
)
from app.services.use_cases.crear_valor_categoria_parametro import (
    CrearValorCategoriaParametro,
)
from app.services.use_cases.listar_valores_categoria_parametro import (
    ListarValoresCategoriaParametro,
)


@lru_cache
def obtener_repositorio_valores_categoria() -> InMemoryValoresCategoriaRepository:
    return InMemoryValoresCategoriaRepository()


def obtener_caso_listar_valores_categoria() -> ListarValoresCategoriaParametro:
    return ListarValoresCategoriaParametro(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_crear_valor_categoria() -> CrearValorCategoriaParametro:
    return CrearValorCategoriaParametro(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_actualizar_valor_categoria() -> ActualizarValorCategoriaParametro:
    return ActualizarValorCategoriaParametro(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_actualizar_estado_valor_categoria(
) -> ActualizarEstadoValorCategoriaParametro:
    return ActualizarEstadoValorCategoriaParametro(
        obtener_repositorio_valores_categoria()
    )

