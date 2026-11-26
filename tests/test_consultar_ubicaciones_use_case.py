import pytest

from app.domain.exceptions.ubicaciones import (
    ParametrosUbicacionInvalidosError,
    PersistenciaUbicacionesError,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.services.use_cases.consultar_ubicaciones_dinamicas import (
    ConsultarUbicacionesDinamicasUseCase,
)


@pytest.fixture
def contexto() -> tuple[
    InMemoryTerritorioRepository, ConsultarUbicacionesDinamicasUseCase
]:
    territorio = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(
        InMemoryDestinoRepository(), territorio
    ).ejecutar()
    return territorio, ConsultarUbicacionesDinamicasUseCase(territorio)


def test_sin_parametros_lista_paises_ordenados(contexto) -> None:
    respuesta = contexto[1].ejecutar()
    assert respuesta.success is True
    assert respuesta.data.nivel == "PAIS"
    assert respuesta.data.id_padre is None
    assert [item.nombre for item in respuesta.data.ubicaciones] == ["Colombia"]


def test_id_pais_lista_departamentos_ordenados(contexto) -> None:
    respuesta = contexto[1].ejecutar(id_pais=1)
    assert respuesta.data.nivel == "DEPARTAMENTO"
    assert [item.nombre for item in respuesta.data.ubicaciones] == [
        "Antioquia",
        "Quindío",
        "Santander",
    ]


def test_id_departamento_lista_solo_municipios_habilitados(contexto) -> None:
    respuesta = contexto[1].ejecutar(id_departamento=63)
    assert respuesta.data.nivel == "MUNICIPIO"
    assert [item.nombre for item in respuesta.data.ubicaciones] == [
        "Armenia",
        "Salento",
    ]


def test_padre_sin_registros_responde_exitoso_falso(contexto) -> None:
    respuesta = contexto[1].ejecutar(id_departamento=9999)
    assert respuesta.success is False
    assert respuesta.mensaje == "No existen ubicaciones para el identificador indicado"
    assert respuesta.data.total == 0
    assert respuesta.data.ubicaciones == []


def test_rechaza_parametros_simultaneos_y_no_positivos(contexto) -> None:
    with pytest.raises(ParametrosUbicacionInvalidosError) as error:
        contexto[1].ejecutar(id_pais=1, id_departamento=63)
    assert str(error.value) == (
        "No se permite enviar id_pais e id_departamento en la misma solicitud"
    )
    with pytest.raises(ParametrosUbicacionInvalidosError):
        contexto[1].ejecutar(id_pais=0)


def test_error_del_repositorio_se_traduce_a_persistencia() -> None:
    class RepoConFallo(InMemoryTerritorioRepository):
        def listar_paises(self):
            raise RuntimeError("fallo de almacenamiento")

    with pytest.raises(PersistenciaUbicacionesError):
        ConsultarUbicacionesDinamicasUseCase(RepoConFallo()).ejecutar()