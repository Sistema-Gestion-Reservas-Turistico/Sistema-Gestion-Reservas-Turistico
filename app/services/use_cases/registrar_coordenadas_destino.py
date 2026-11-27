import math

from app.domain.exceptions.destino import (
    CoincidenciaTerritorialError,
    CoordenadasFueraDeRangoError,
    DestinoNoEncontradoError,
    PersistenciaCoordenadasError,
)
from app.domain.interfaces.destino import DestinoRepository
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.destino import (
    RegistrarCoordenadasDestinoCreate,
    RegistrarCoordenadasDestinoResponse,
)


class RegistrarCoordenadasDestinoUseCase:
    def __init__(
        self,
        destinos: DestinoRepository,
        territorios: TerritorioRepository,
    ) -> None:
        self._destinos = destinos
        self._territorios = territorios

    def ejecutar(
        self,
        id_destino: int,
        datos: RegistrarCoordenadasDestinoCreate,
    ) -> RegistrarCoordenadasDestinoResponse:
        if not math.isfinite(datos.latitud) or not -90 <= datos.latitud <= 90:
            raise CoordenadasFueraDeRangoError("latitud")
        if not math.isfinite(datos.longitud) or not -180 <= datos.longitud <= 180:
            raise CoordenadasFueraDeRangoError("longitud")

        try:
            destino = self._destinos.obtener_por_id(id_destino)
        except Exception as error:
            raise PersistenciaCoordenadasError() from error
        if destino is None:
            raise DestinoNoEncontradoError()

        try:
            pertenece = self._territorios.coordenadas_pertenecen_municipio(
                destino.id_municipio,
                datos.latitud,
                datos.longitud,
            )
        except Exception as error:
            raise PersistenciaCoordenadasError() from error
        if not pertenece:
            raise CoincidenciaTerritorialError()

        try:
            actualizado = self._destinos.actualizar_coordenadas(
                id_destino,
                datos.latitud,
                datos.longitud,
            )
        except DestinoNoEncontradoError:
            raise
        except Exception as error:
            raise PersistenciaCoordenadasError() from error
        return RegistrarCoordenadasDestinoResponse.desde_destino(actualizado)