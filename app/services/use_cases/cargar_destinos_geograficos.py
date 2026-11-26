from app.domain.entities.destino import Destino
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.interfaces.destino import DestinoRepository
from app.domain.interfaces.territorio import TerritorioRepository


class CargarDestinosGeograficosUseCase:
    def __init__(
        self,
        destinos: DestinoRepository,
        territorios: TerritorioRepository,
    ) -> None:
        self._destinos = destinos
        self._territorios = territorios

    def ejecutar(self) -> None:
        self._territorios.crear_municipio_si_no_existe(
            MunicipioTerritorial(
                id_municipio=63690,
                latitud_min=4.55,
                latitud_max=4.72,
                longitud_min=-75.66,
                longitud_max=-75.46,
            )
        )
        self._destinos.crear_si_no_existe(
            Destino(
                id_destino=15,
                nombre="Reserva Natural Demo",
                id_municipio=63690,
            )
        )