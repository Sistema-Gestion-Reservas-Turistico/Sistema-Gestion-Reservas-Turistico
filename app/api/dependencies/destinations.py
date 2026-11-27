from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.repositories.adapters.in_memory_destinations_repository import (
    InMemoryDestinationRepository,
)
from app.repositories.adapters.in_memory_municipalities_repository import (
    InMemoryMunicipalityRepository,
)
from app.services.use_cases.cargar_parametros_turismo import CargarParametrosTurismo
from app.services.use_cases.save_destination import SaveDestinationUseCase


@lru_cache
def obtener_repositorio_destinos() -> InMemoryDestinationRepository:
    return InMemoryDestinationRepository()


@lru_cache
def obtener_repositorio_municipios() -> InMemoryMunicipalityRepository:
    return InMemoryMunicipalityRepository()


def obtener_caso_guardar_destino() -> SaveDestinationUseCase:
    return SaveDestinationUseCase(
        obtener_repositorio_destinos(),
        obtener_repositorio_municipios(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_cargar_parametros_turismo() -> CargarParametrosTurismo:
    return CargarParametrosTurismo(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )
