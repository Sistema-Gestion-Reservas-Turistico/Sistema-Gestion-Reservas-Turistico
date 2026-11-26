from app.domain.entities.destino import Destino
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.exceptions.destino import CoordenadasFueraDeRangoError
from app.domain.models.destino import RegistrarCoordenadasDestinoResponse


def test_destino_comienza_sin_coordenadas() -> None:
    destino = Destino(15, "Reserva Natural Demo", 63690)
    assert destino.latitud is None
    assert destino.longitud is None
    assert destino.estado_coordenadas == "PENDIENTES"


def test_respuesta_conserva_coordenadas_y_estado() -> None:
    destino = Destino(
        15,
        "Reserva Natural Demo",
        63690,
        4.6372,
        -75.5712,
        "REGISTRADAS",
    )
    respuesta = RegistrarCoordenadasDestinoResponse.desde_destino(destino)
    assert respuesta.data.id_destino == 15
    assert respuesta.data.estado_coordenadas == "REGISTRADAS"


def test_error_de_rango_indica_campo() -> None:
    assert str(CoordenadasFueraDeRangoError("latitud")) == (
        "La latitud debe estar entre -90 y 90"
    )
    assert str(CoordenadasFueraDeRangoError("longitud")) == (
        "La longitud debe estar entre -180 y 180"
    )


def test_municipio_guarda_limites_de_coordenadas() -> None:
    municipio = MunicipioTerritorial(63690, 4.55, 4.72, -75.66, -75.46)
    assert municipio.id_municipio == 63690