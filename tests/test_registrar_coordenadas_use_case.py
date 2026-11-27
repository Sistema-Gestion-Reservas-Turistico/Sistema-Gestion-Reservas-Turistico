import pytest

from app.domain.entities.destino import Destino
from app.domain.exceptions.destino import (
    CoincidenciaTerritorialError,
    CoordenadasFueraDeRangoError,
    DestinoNoEncontradoError,
    PersistenciaCoordenadasError,
)
from app.domain.models.destino import RegistrarCoordenadasDestinoCreate
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)
from app.services.use_cases.registrar_coordenadas_destino import (
    RegistrarCoordenadasDestinoUseCase,
)


@pytest.fixture
def contexto() -> tuple[
    InMemoryDestinoRepository,
    InMemoryTerritorioRepository,
    RegistrarCoordenadasDestinoUseCase,
]:
    destinos = InMemoryDestinoRepository()
    territorios = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(destinos, territorios).ejecutar()
    caso = RegistrarCoordenadasDestinoUseCase(destinos, territorios)
    return destinos, territorios, caso


def test_registra_y_sobrescribe_coordenadas(contexto) -> None:
    destinos, _, caso = contexto
    respuesta = caso.ejecutar(
        15, RegistrarCoordenadasDestinoCreate(4.6372, -75.5712)
    )
    assert respuesta.data.id_destino == 15
    assert respuesta.data.estado_coordenadas == "REGISTRADAS"

    actualizada = caso.ejecutar(
        15, RegistrarCoordenadasDestinoCreate(4.64, -75.57)
    )
    almacenada = destinos.obtener_por_id(15)
    assert actualizada.data.latitud == 4.64
    assert almacenada.longitud == -75.57


@pytest.mark.parametrize(
    ("datos", "campo"),
    [
        (RegistrarCoordenadasDestinoCreate(90.1, 0), "latitud"),
        (RegistrarCoordenadasDestinoCreate(0, -180.1), "longitud"),
        (RegistrarCoordenadasDestinoCreate(float("nan"), 0), "latitud"),
    ],
)
def test_rechaza_coordenadas_fuera_de_rango(contexto, datos, campo) -> None:
    with pytest.raises(CoordenadasFueraDeRangoError) as error:
        contexto[2].ejecutar(15, datos)
    assert error.value.campo == campo


def test_destino_inexistente_da_error_de_dominio(contexto) -> None:
    with pytest.raises(DestinoNoEncontradoError):
        contexto[2].ejecutar(999, RegistrarCoordenadasDestinoCreate(4.6372, -75.5712))


def test_coordenadas_fuera_del_municipio_da_conflicto(contexto) -> None:
    with pytest.raises(CoincidenciaTerritorialError):
        contexto[2].ejecutar(15, RegistrarCoordenadasDestinoCreate(4.8, -75.5712))


def test_error_del_repositorio_se_traduce_a_persistencia() -> None:
    class RepoConFallo(InMemoryDestinoRepository):
        def obtener_por_id(self, id_destino: int):
            raise RuntimeError("fallo de almacenamiento")

    caso = RegistrarCoordenadasDestinoUseCase(
        RepoConFallo(), InMemoryTerritorioRepository()
    )
    with pytest.raises(PersistenciaCoordenadasError):
        caso.ejecutar(15, RegistrarCoordenadasDestinoCreate(4.6372, -75.5712))