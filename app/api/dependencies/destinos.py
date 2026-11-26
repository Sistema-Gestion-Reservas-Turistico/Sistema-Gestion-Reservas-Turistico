from functools import lru_cache

from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)
from app.services.use_cases.consultar_ubicaciones_dinamicas import (
    ConsultarUbicacionesDinamicasUseCase,
)
from app.services.use_cases.registrar_coordenadas_destino import (
    RegistrarCoordenadasDestinoUseCase,
)


@lru_cache
def obtener_repositorio_destinos() -> InMemoryDestinoRepository:
    return InMemoryDestinoRepository()


@lru_cache
def obtener_repositorio_territorios() -> InMemoryTerritorioRepository:
    return InMemoryTerritorioRepository()


def obtener_caso_registrar_coordenadas_destino() -> (
    RegistrarCoordenadasDestinoUseCase
):
    return RegistrarCoordenadasDestinoUseCase(
        obtener_repositorio_destinos(),
        obtener_repositorio_territorios(),
    )


def obtener_caso_cargar_destinos_geograficos() -> CargarDestinosGeograficosUseCase:
    return CargarDestinosGeograficosUseCase(
        obtener_repositorio_destinos(),
        obtener_repositorio_territorios(),
    )


def obtener_caso_consultar_ubicaciones_dinamicas() -> (
    ConsultarUbicacionesDinamicasUseCase
):
    return ConsultarUbicacionesDinamicasUseCase(
        obtener_repositorio_territorios()
    )