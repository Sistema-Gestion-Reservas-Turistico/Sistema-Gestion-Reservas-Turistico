import pytest

from app.domain.entities.departamento import Departamento
from app.domain.entities.pais import Pais
from app.domain.exceptions.estructura_territorial import (
    ParametrosEstructuraInvalidosError,
    PersistenciaEstructuraTerritorialError,
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
from app.services.use_cases.consultar_estructura_territorial import (
    ConsultarEstructuraTerritorialUseCase,
)


@pytest.fixture
def contexto() -> tuple[
    InMemoryTerritorioRepository, ConsultarEstructuraTerritorialUseCase
]:
    territorio = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(
        InMemoryDestinoRepository(), territorio
    ).ejecutar()
    return territorio, ConsultarEstructuraTerritorialUseCase(territorio)


def test_consulta_incluye_todos_los_municipios_y_orden_alfabetico(contexto) -> None:
    respuesta = contexto[1].ejecutar("1", "63")

    assert respuesta.success is True
    assert respuesta.mensaje == "Consulta de estructura territorial exitosa"
    assert respuesta.data.nombre == "Colombia"
    assert respuesta.data.total_departamentos == 1
    assert respuesta.data.total_municipios == 3
    departamento = respuesta.data.departamentos[0]
    assert (departamento.id, departamento.nombre) == (63, "Quindío")
    assert [
        (municipio.nombre, municipio.habilitado)
        for municipio in departamento.municipios
    ] == [
        ("Armenia", True),
        ("Calarcá", False),
        ("Salento", True),
    ]


def test_consulta_pais_agrupa_departamentos_y_municipios(contexto) -> None:
    respuesta = contexto[1].ejecutar(1)

    assert respuesta.data.total_departamentos == 4
    assert respuesta.data.total_municipios == 4
    assert [
        departamento.nombre for departamento in respuesta.data.departamentos
    ] == ["Antioquia", "Caldas", "Quindío", "Santander"]
    assert respuesta.data.departamentos[1].municipios[0].nombre == "Salamina"


@pytest.mark.parametrize("id_pais", [None, "", "abc", 0, -1])
def test_id_pais_ausente_o_invalido_se_rechaza(contexto, id_pais) -> None:
    with pytest.raises(ParametrosEstructuraInvalidosError) as error:
        contexto[1].ejecutar(id_pais)

    assert str(error.value) == (
        "El identificador del país es obligatorio y debe ser numérico"
    )


@pytest.mark.parametrize("id_departamento", ["abc", "", 0, -1])
def test_id_departamento_invalido_se_rechaza(contexto, id_departamento) -> None:
    with pytest.raises(ParametrosEstructuraInvalidosError) as error:
        contexto[1].ejecutar("1", id_departamento)

    assert str(error.value) == (
        "El identificador del departamento debe ser numérico"
    )


@pytest.mark.parametrize(
    ("id_pais", "id_departamento"),
    [("9999", None), ("1", "9999")],
)
def test_sin_estructura_retorna_respuesta_vacia(
    contexto, id_pais: str, id_departamento: str | None
) -> None:
    respuesta = contexto[1].ejecutar(id_pais, id_departamento)

    assert respuesta.success is False
    assert respuesta.mensaje == (
        "No existe estructura territorial para el país indicado"
    )
    assert respuesta.data.id_pais == int(id_pais)
    assert respuesta.data.nombre is None
    assert respuesta.data.total_departamentos == 0
    assert respuesta.data.total_municipios == 0
    assert respuesta.data.departamentos == []


def test_pais_existente_sin_departamentos_retorna_respuesta_vacia() -> None:
    territorio = InMemoryTerritorioRepository()
    territorio.crear_pais_si_no_existe(Pais(2, "Otro país"))

    respuesta = ConsultarEstructuraTerritorialUseCase(territorio).ejecutar(2)

    assert respuesta.success is False
    assert respuesta.data.nombre is None
    assert respuesta.data.departamentos == []


def test_consulta_con_fallo_del_repositorio_se_traduce_a_persistencia() -> None:
    class RepoConFallo(InMemoryTerritorioRepository):
        def consultar_estructura_territorial(self, id_pais, id_departamento=None):
            assert id_pais == 1
            assert id_departamento is None
            raise RuntimeError("fallo de almacenamiento")

    caso = ConsultarEstructuraTerritorialUseCase(RepoConFallo())

    with pytest.raises(PersistenciaEstructuraTerritorialError) as error:
        caso.ejecutar(1)

    assert str(error.value) == (
        "No fue posible consultar la estructura territorial"
    )


def test_repositorio_no_incluye_departamento_ajeno_al_pais(contexto) -> None:
    territorio = contexto[0]
    territorio.crear_pais_si_no_existe(Pais(2, "Otro país"))
    territorio.crear_departamento_si_no_existe(
        Departamento(99, 2, "Departamento externo")
    )

    pais, estructura = territorio.consultar_estructura_territorial(1, 99)

    assert pais == Pais(1, "Colombia")
    assert estructura == []
