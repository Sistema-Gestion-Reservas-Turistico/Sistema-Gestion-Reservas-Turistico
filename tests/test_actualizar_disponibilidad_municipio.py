from datetime import datetime, timedelta, timezone

import pytest

from app.domain.entities.destino import Destino
from app.domain.exceptions.disponibilidad_municipio import (
    DisponibilidadMunicipioInvalidaError,
    MunicipioNoEncontradoError,
    PersistenciaMunicipioError,
)
from app.domain.models.disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioCreate,
)
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.actualizar_disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioUseCase,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)


@pytest.fixture
def contexto():
    destinos = InMemoryDestinoRepository()
    territorio = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(destinos, territorio).ejecutar()
    return destinos, territorio, ActualizarDisponibilidadMunicipioUseCase(territorio)


def test_cambiar_estado_actualiza_fecha_y_preserva_destinos(contexto) -> None:
    destinos, territorio, caso = contexto
    momento = datetime(2026, 10, 25, 15, 10, tzinfo=timezone.utc)
    respuesta = caso.ejecutar(
        63130, ActualizarDisponibilidadMunicipioCreate(True), momento
    )
    municipio = territorio.obtener_municipio(63130)
    assert respuesta.mensaje == "Disponibilidad del municipio actualizada exitosamente"
    assert respuesta.data.habilitado is True
    assert respuesta.data.fecha_actualizacion.endswith("-05:00")
    assert municipio.fecha_actualizacion.utcoffset() == -timedelta(hours=5)
    assert destinos.obtener_por_id(15) is not None


def test_mismo_estado_no_modifica_fecha(contexto) -> None:
    _, territorio, caso = contexto
    fecha_original = territorio.obtener_municipio(63130).fecha_actualizacion
    respuesta = caso.ejecutar(
        63130,
        ActualizarDisponibilidadMunicipioCreate(False),
        datetime(2026, 11, 25, tzinfo=timezone.utc),
    )
    assert respuesta.mensaje == (
        "El municipio ya se encontraba en el estado solicitado (sin cambios)"
    )
    assert territorio.obtener_municipio(63130).fecha_actualizacion == fecha_original


@pytest.mark.parametrize("valor", (None, "si", 1, 0))
def test_habilitado_debe_ser_booleano_estricto(contexto, valor) -> None:
    with pytest.raises(DisponibilidadMunicipioInvalidaError):
        contexto[2].ejecutar(
            63130, ActualizarDisponibilidadMunicipioCreate(valor)
        )


def test_municipio_inexistente_da_error_de_dominio(contexto) -> None:
    with pytest.raises(MunicipioNoEncontradoError):
        contexto[2].ejecutar(99999, ActualizarDisponibilidadMunicipioCreate(True))


def test_error_de_repositorio_se_traduce_a_persistencia() -> None:
    class RepoConFallo(InMemoryTerritorioRepository):
        def obtener_municipio(self, id_municipio: int):
            raise RuntimeError("fallo de almacenamiento")

    with pytest.raises(PersistenciaMunicipioError):
        ActualizarDisponibilidadMunicipioUseCase(RepoConFallo()).ejecutar(
            63130, ActualizarDisponibilidadMunicipioCreate(True)
        )