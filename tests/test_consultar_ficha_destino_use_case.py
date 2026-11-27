import pytest

from app.domain.entities.destino import Destino
from app.domain.exceptions.ficha_destino import (
    DestinoActivoNoEncontradoError,
    IdentificadorDestinoInvalidoError,
    PersistenciaFichaDestinoError,
)
from app.repositories.adapters.in_memory_destino_repository import (
    InMemoryDestinoRepository,
)
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)
from app.services.use_cases.cargar_destinos_geograficos import (
    CargarDestinosGeograficosUseCase,
)
from app.services.use_cases.consultar_ficha_destino import (
    ConsultarFichaDestinoUseCase,
)


@pytest.fixture
def contexto() -> tuple[
    InMemoryDestinoRepository,
    InMemoryTerritorioRepository,
    ConsultarFichaDestinoUseCase,
]:
    destinos = InMemoryDestinoRepository()
    territorios = InMemoryTerritorioRepository()
    CargarDestinosGeograficosUseCase(destinos, territorios).ejecutar()
    caso = ConsultarFichaDestinoUseCase(destinos, territorios)
    return destinos, territorios, caso


def test_ficha_destino_activo_sin_coordenadas(contexto) -> None:
    respuesta = contexto[2].ejecutar("15")

    assert respuesta.success is True
    assert respuesta.mensaje == "Consulta de ficha de destino exitosa"
    assert respuesta.data.id_destino == 15
    assert respuesta.data.nombre == "Reserva Natural Demo"
    assert respuesta.data.descripcion == (
        "Reserva natural con senderos ecológicos y miradores."
    )
    assert respuesta.data.ubicacion.municipio == "Salento"
    assert respuesta.data.ubicacion.departamento == "Quindío"
    assert respuesta.data.ubicacion.pais == "Colombia"
    assert respuesta.data.tipos_turismo == ["AVENTURA", "ECOTURISMO"]
    assert [
        (actividad.id, actividad.nombre)
        for actividad in respuesta.data.actividades
    ] == [(1, "Senderismo"), (2, "Observación de aves")]
    assert respuesta.data.coordenadas is None
    assert respuesta.data.imagen_principal_url == (
        "https://almacenamiento.ejemplo.com/destinos/15.jpg"
    )


def test_ficha_destino_activo_con_coordenadas(contexto) -> None:
    contexto[0].actualizar_coordenadas(15, 4.6372, -75.5712)

    respuesta = contexto[2].ejecutar(15)

    assert respuesta.data.coordenadas is not None
    assert respuesta.data.coordenadas.latitud == 4.6372
    assert respuesta.data.coordenadas.longitud == -75.5712


@pytest.mark.parametrize("id_destino", ["abc", "", "0", "-1", 0, -1])
def test_identificador_invalido_se_rechaza(contexto, id_destino) -> None:
    with pytest.raises(IdentificadorDestinoInvalidoError) as error:
        contexto[2].ejecutar(id_destino)

    assert str(error.value) == "El identificador del destino no es válido"


@pytest.mark.parametrize("id_destino", [9999, 16])
def test_destino_inexistente_o_inactivo_se_rechaza(contexto, id_destino) -> None:
    with pytest.raises(DestinoActivoNoEncontradoError) as error:
        contexto[2].ejecutar(id_destino)

    assert str(error.value) == (
        "No existe un destino activo con el identificador indicado"
    )


def test_jerarquia_territorial_no_disponible_se_traduce_a_persistencia(
    contexto,
) -> None:
    contexto[0].crear_si_no_existe(
        Destino(17, "Sin ubicación", id_municipio=9999)
    )

    with pytest.raises(PersistenciaFichaDestinoError):
        contexto[2].ejecutar(17)


def test_fallo_al_consultar_destino_se_traduce_a_persistencia() -> None:
    class DestinosConFallo(InMemoryDestinoRepository):
        def obtener_por_id(self, id_destino: int):
            assert id_destino == 15
            raise RuntimeError("fallo de almacenamiento")

    caso = ConsultarFichaDestinoUseCase(
        DestinosConFallo(), InMemoryTerritorioRepository()
    )

    with pytest.raises(PersistenciaFichaDestinoError) as error:
        caso.ejecutar("15")

    assert str(error.value) == "No fue posible consultar la ficha del destino"


def test_fallo_al_resolver_territorio_se_traduce_a_persistencia(contexto) -> None:
    class TerritorioConFallo(InMemoryTerritorioRepository):
        def obtener_jerarquia_municipio(self, id_municipio: int):
            assert id_municipio == 63690
            raise RuntimeError("fallo de almacenamiento")

    caso = ConsultarFichaDestinoUseCase(contexto[0], TerritorioConFallo())

    with pytest.raises(PersistenciaFichaDestinoError):
        caso.ejecutar(15)


def test_seed_enriquece_destino_y_preserva_coordenadas_iniciales(contexto) -> None:
    destinos = contexto[0]
    principal = destinos.obtener_por_id(15)
    inactivo = destinos.obtener_por_id(16)

    assert principal is not None
    assert principal.latitud is None
    assert principal.longitud is None
    assert principal.activo is True
    assert inactivo is not None
    assert inactivo.activo is False
