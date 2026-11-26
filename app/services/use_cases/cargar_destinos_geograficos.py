from app.domain.entities.destino import Destino
from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.interfaces.destino import DestinoRepository
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.entities.pais import Pais


class CargarDestinosGeograficosUseCase:
    def __init__(
        self,
        destinos: DestinoRepository,
        territorios: TerritorioRepository,
    ) -> None:
        self._destinos = destinos
        self._territorios = territorios

    def ejecutar(self) -> None:
        self._territorios.crear_pais_si_no_existe(Pais(1, "Colombia"))
        for departamento in (
            Departamento(5, 1, "Antioquia"),
            Departamento(63, 1, "Quindío"),
            Departamento(68, 1, "Santander"),
        ):
            self._territorios.crear_departamento_si_no_existe(departamento)

        for municipio in (
            MunicipioTerritorial(
                id_municipio=63001,
                latitud_min=4.50,
                latitud_max=4.57,
                longitud_min=-75.72,
                longitud_max=-75.64,
                nombre="Armenia",
                id_departamento=63,
            ),
            MunicipioTerritorial(
                id_municipio=63690,
                latitud_min=4.55,
                latitud_max=4.72,
                longitud_min=-75.66,
                longitud_max=-75.46,
                nombre="Salento",
                id_departamento=63,
            ),
            MunicipioTerritorial(
                id_municipio=63130,
                latitud_min=4.48,
                latitud_max=4.57,
                longitud_min=-75.72,
                longitud_max=-75.60,
                nombre="Calarcá",
                id_departamento=63,
                habilitado=False,
            ),
        ):
            self._territorios.crear_municipio_si_no_existe(municipio)

        self._destinos.crear_si_no_existe(
            Destino(
                id_destino=15,
                nombre="Reserva Natural Demo",
                id_municipio=63690,
            )
        )