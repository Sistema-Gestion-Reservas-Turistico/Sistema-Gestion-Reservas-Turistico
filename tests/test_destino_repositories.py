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
    assert [pais.nombre for pais in territorios.listar_paises()] == ["Colombia"]
    assert [
        departamento.nombre
        for departamento in territorios.listar_departamentos_por_pais(1)
    ] == ["Antioquia", "Quindío", "Santander", "Caldas"]
    assert [
        municipio.nombre
        for municipio in territorios.listar_municipios_por_departamento(63)
    ] == ["Armenia", "Salento"]
    sugerencias = territorios.listar_ubicaciones_autocompletar()
    assert not any(item.nombre == "Calarcá" for item in sugerencias)
    assert any(
        item.nombre == "Salento" and item.departamento == "Quindío"
        for item in sugerencias
    )
    assert any(
        item.nombre == "Salamina" and item.departamento == "Caldas"
        for item in sugerencias
    )


def test_seed_no_reemplaza_destino_existente() -> None:
    destinos = InMemoryDestinoRepository()
    destinos.crear_si_no_existe(Destino(15, "Nombre existente", 63690))
    CargarDestinosGeograficosUseCase(
        destinos, InMemoryTerritorioRepository()
    ).ejecutar()
    assert destinos.obtener_por_id(15).nombre == "Nombre existente"