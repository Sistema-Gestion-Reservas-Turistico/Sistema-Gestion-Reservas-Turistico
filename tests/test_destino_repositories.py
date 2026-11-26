from app.domain.entities.destino import Destino
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)


def test_seed_es_idempotente_y_punto_de_salento_es_valido() -> None:
    destinos = InMemoryDestinoRepository()
    territorios = InMemoryTerritorioRepository()
    cargar = CargarDestinosGeograficosUseCase(destinos, territorios)
    cargar.ejecutar()
    cargar.ejecutar()

    destino = destinos.obtener_por_id(15)
    assert destino is not None
    assert destino.nombre == "Reserva Natural Demo"
    assert territorios.coordenadas_pertenecen_municipio(
        63690, 4.6372, -75.5712
    )
    assert not territorios.coordenadas_pertenecen_municipio(
        63690, 4.8, -75.5712
    )


def test_seed_no_reemplaza_destino_existente() -> None:
    destinos = InMemoryDestinoRepository()
    destinos.crear_si_no_existe(Destino(15, "Nombre existente", 63690))
    CargarDestinosGeograficosUseCase(
        destinos, InMemoryTerritorioRepository()
    ).ejecutar()
    assert destinos.obtener_por_id(15).nombre == "Nombre existente"