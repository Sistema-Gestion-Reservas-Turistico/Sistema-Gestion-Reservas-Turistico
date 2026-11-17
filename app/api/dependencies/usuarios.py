from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.repositories.adapters.in_memory_usuario_repository import (
    InMemoryUsuarioRepository,
)
from app.services.use_cases.cargar_parametros_usuarios import CargarParametrosUsuarios
from app.services.use_cases.registrar_usuario import RegistrarUsuarioUseCase


@lru_cache
def obtener_repositorio_usuarios() -> InMemoryUsuarioRepository:
    return InMemoryUsuarioRepository()


def obtener_caso_registrar_usuario() -> RegistrarUsuarioUseCase:
    return RegistrarUsuarioUseCase(
        obtener_repositorio_usuarios(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_cargar_parametros_usuarios() -> CargarParametrosUsuarios:
    return CargarParametrosUsuarios(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )
