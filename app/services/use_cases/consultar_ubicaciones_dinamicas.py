from app.domain.exceptions.ubicaciones import (
    ParametrosUbicacionInvalidosError,
    PersistenciaUbicacionesError,
)
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.ubicaciones import (
    ConsultaUbicacionesData,
    ConsultaUbicacionesResponse,
    UbicacionItem,
)


_ERROR_ID = "El identificador de ubicación debe ser numérico"
_ERROR_PARAMETROS = (
    "No se permite enviar id_pais e id_departamento en la misma solicitud"
)


class ConsultarUbicacionesDinamicasUseCase:
    def __init__(self, territorio: TerritorioRepository) -> None:
        self._territorio = territorio

    def ejecutar(
        self,
        id_pais: int | None = None,
        id_departamento: int | None = None,
    ) -> ConsultaUbicacionesResponse:
        if id_pais is not None and id_departamento is not None:
            raise ParametrosUbicacionInvalidosError(_ERROR_PARAMETROS)
        if any(
            identificador is not None and identificador <= 0
            for identificador in (id_pais, id_departamento)
        ):
            raise ParametrosUbicacionInvalidosError(_ERROR_ID)

        try:
            if id_pais is None and id_departamento is None:
                nivel = "PAIS"
                id_padre = None
                ubicaciones = [
                    UbicacionItem(item.id, item.nombre)
                    for item in self._territorio.listar_paises()
                ]
            elif id_pais is not None:
                nivel = "DEPARTAMENTO"
                id_padre = id_pais
                ubicaciones = [
                    UbicacionItem(item.id, item.nombre)
                    for item in self._territorio.listar_departamentos_por_pais(
                        id_pais
                    )
                ]
            else:
                nivel = "MUNICIPIO"
                id_padre = id_departamento
                ubicaciones = [
                    UbicacionItem(item.id_municipio, item.nombre)
                    for item in self._territorio.listar_municipios_por_departamento(
                        id_departamento
                    )
                ]
        except Exception as error:
            raise PersistenciaUbicacionesError() from error

        ubicaciones.sort(key=lambda item: item.nombre.casefold())
        total = len(ubicaciones)
        if total:
            return ConsultaUbicacionesResponse(
                mensaje="Consulta de ubicaciones exitosa",
                data=ConsultaUbicacionesData(nivel, id_padre, total, ubicaciones),
                success=True,
            )
        return ConsultaUbicacionesResponse(
            mensaje="No existen ubicaciones para el identificador indicado",
            data=ConsultaUbicacionesData(nivel, id_padre, 0, []),
            success=False,
        )