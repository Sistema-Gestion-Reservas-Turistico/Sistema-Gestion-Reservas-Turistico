from app.domain.entities.destino import ActividadDestino, Destino
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
            Departamento(17, 1, "Caldas"),
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
            MunicipioTerritorial(
                id_municipio=17653,
                latitud_min=5.35,
                latitud_max=5.45,
                longitud_min=-75.10,
                longitud_max=-74.95,
                nombre="Salamina",
                id_departamento=17,
            ),
        ):
            self._territorios.crear_municipio_si_no_existe(municipio)

        self._destinos.crear_si_no_existe(
            Destino(
                id_destino=15,
                nombre="Reserva Natural Demo",
                id_municipio=63690,
                descripcion=(
                    "Reserva natural con senderos ecológicos y miradores."
                ),
                tipos_turismo=["AVENTURA", "ECOTURISMO"],
                actividades=[
                    ActividadDestino(id=1, nombre="Senderismo"),
                    ActividadDestino(
                        id=2, nombre="Observación de aves"
                    ),
                ],
                imagen_principal_url=(
                    "https://almacenamiento.ejemplo.com/destinos/15.jpg"
                ),
                activo=True,
            )
        )
        self._destinos.crear_si_no_existe(
            Destino(
                id_destino=16,
                nombre="Destino inactivo Demo",
                id_municipio=63690,
                activo=False,
            )
        )