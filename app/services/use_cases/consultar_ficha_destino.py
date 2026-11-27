from app.domain.exceptions.ficha_destino import (
    DestinoActivoNoEncontradoError,
    IdentificadorDestinoInvalidoError,
    PersistenciaFichaDestinoError,
)
from app.domain.interfaces.destino import DestinoRepository
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.ficha_destino import (
    ActividadDestinoItem,
    CoordenadasDestinoItem,
    FichaDestinoData,
    FichaDestinoResponse,
    UbicacionDestinoData,
)


class ConsultarFichaDestinoUseCase:
    def __init__(
        self,
        destinos: DestinoRepository,
        territorios: TerritorioRepository,
    ) -> None:
        self._destinos = destinos
        self._territorios = territorios

    def ejecutar(self, id_destino: int | str) -> FichaDestinoResponse:
        id_validado = self._validar_id_destino(id_destino)
        try:
            destino = self._destinos.obtener_por_id(id_validado)
        except Exception as error:
            raise PersistenciaFichaDestinoError() from error

        if destino is None or not destino.activo:
            raise DestinoActivoNoEncontradoError()

        try:
            jerarquia = self._territorios.obtener_jerarquia_municipio(
                destino.id_municipio
            )
            if jerarquia is None:
                raise ValueError(
                    "No se encontró la jerarquía territorial del destino"
                )
            municipio, departamento, pais = jerarquia
        except Exception as error:
            raise PersistenciaFichaDestinoError() from error

        coordenadas = None
        if destino.latitud is not None and destino.longitud is not None:
            coordenadas = CoordenadasDestinoItem(
                latitud=destino.latitud,
                longitud=destino.longitud,
            )

        return FichaDestinoResponse(
            mensaje="Consulta de ficha de destino exitosa",
            data=FichaDestinoData(
                id_destino=destino.id_destino,
                nombre=destino.nombre,
                descripcion=destino.descripcion,
                ubicacion=UbicacionDestinoData(
                    municipio=municipio.nombre,
                    departamento=departamento.nombre,
                    pais=pais.nombre,
                ),
                tipos_turismo=list(destino.tipos_turismo),
                actividades=[
                    ActividadDestinoItem(id=actividad.id, nombre=actividad.nombre)
                    for actividad in destino.actividades
                ],
                coordenadas=coordenadas,
                imagen_principal_url=destino.imagen_principal_url,
            ),
            success=True,
        )

    @staticmethod
    def _validar_id_destino(id_destino: int | str) -> int:
        if isinstance(id_destino, bool) or not isinstance(
            id_destino, (int, str)
        ):
            raise IdentificadorDestinoInvalidoError()
        try:
            id_validado = int(id_destino)
        except (TypeError, ValueError) as error:
            raise IdentificadorDestinoInvalidoError() from error
        if id_validado <= 0:
            raise IdentificadorDestinoInvalidoError()
        return id_validado
