import pytest

from app.domain.entities.sugerencia_territorial import SugerenciaTerritorial
from app.domain.exceptions.autocompletar_ubicaciones import (
    ConsultaAutocompletarInvalidaError,
    PersistenciaAutocompletarError,
)
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.autocompletar_ubicaciones import (
    AutocompletarUbicacionesUseCase,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)


@pytest.fixture
def contexto() -> tuple[
    InMemoryTerritorioRepository, AutocompletarUbicacionesUseCase
]:
    territorio = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(
        InMemoryDestinoRepository(), territorio
    ).ejecutar()
    return territorio, AutocompletarUbicacionesUseCase(territorio)


def test_sal_busca_salento_y_salamina_con_departamento(contexto) -> None:
    respuesta = contexto[1].ejecutar("sal", 5)
    assert respuesta.success is True
    assert respuesta.mensaje == "Sugerencias de ubicación encontradas"
    assert [
        (item.nombre, item.departamento) for item in respuesta.data.sugerencias
    ] == [("Salamina", "Caldas"), ("Salento", "Quindío")]


def test_busqueda_no_distingue_tildes_mayusculas_ni_posicion(contexto) -> None:
    departamentos = contexto[1].ejecutar("QUINDIO")
    assert [item.nombre for item in departamentos.data.sugerencias] == ["Quindío"]
    parcial = contexto[1].ejecutar("tio")
    assert "Antioquia" in [item.nombre for item in parcial.data.sugerencias]


def test_prefijos_tienen_prioridad_sobre_coincidencias_internas() -> None:
    class RepoOrden:
        def listar_ubicaciones_autocompletar(self):
            return [
                SugerenciaTerritorial(1, "Zaragoza", "DEPARTAMENTO"),
                SugerenciaTerritorial(2, "Aragón", "DEPARTAMENTO"),
                SugerenciaTerritorial(3, "Arawak", "MUNICIPIO", "Caldas"),
            ]

    respuesta = AutocompletarUbicacionesUseCase(RepoOrden()).ejecutar("ara")
    assert [item.nombre for item in respuesta.data.sugerencias] == [
        "Aragón",
        "Arawak",
        "Zaragoza",
    ]


@pytest.mark.parametrize("q", (None, "", "  ", "ab", "  ab  "))
def test_consulta_corta_o_ausente_es_invalida(contexto, q) -> None:
    with pytest.raises(ConsultaAutocompletarInvalidaError):
        contexto[1].ejecutar(q)


@pytest.mark.parametrize("limite", (0, -1, 1.5, True))
def test_limite_invalido_es_rechazado(contexto, limite) -> None:
    with pytest.raises(ConsultaAutocompletarInvalidaError):
        contexto[1].ejecutar("sal", limite)


def test_limite_se_aplica_despues_de_ordenar(contexto) -> None:
    respuesta = contexto[1].ejecutar("sal", 1)
    assert respuesta.data.total == 1
    assert respuesta.data.sugerencias[0].nombre == "Salamina"


def test_sin_coincidencias_devuelve_lista_vacia(contexto) -> None:
    respuesta = contexto[1].ejecutar("xyz")
    assert respuesta.success is False
    assert respuesta.mensaje == (
        "No se encontraron ubicaciones que coincidan con el texto ingresado"
    )
    assert respuesta.data.total == 0
    assert respuesta.data.sugerencias == []


def test_error_de_repositorio_se_traduce_a_persistencia() -> None:
    class RepoConFallo:
        def listar_ubicaciones_autocompletar(self):
            raise RuntimeError("fallo de almacenamiento")

    with pytest.raises(PersistenciaAutocompletarError):
        AutocompletarUbicacionesUseCase(RepoConFallo()).ejecutar("sal")