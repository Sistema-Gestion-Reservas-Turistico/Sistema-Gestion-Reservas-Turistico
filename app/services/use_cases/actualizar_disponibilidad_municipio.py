from datetime import datetime, timedelta, timezone

from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.exceptions.disponibilidad_municipio import (
    DisponibilidadMunicipioInvalidaError,
    MunicipioNoEncontradoError,
    PersistenciaMunicipioError,
)
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.disponibilidad_municipio import (
    ActualizarDisponibilidadMunicipioCreate,
    DisponibilidadMunicipioData,
    DisponibilidadMunicipioResponse,
)


_ZONA_HORARIA_COLOMBIA = timezone(timedelta(hours=-5))


class ActualizarDisponibilidadMunicipioUseCase:
    def __init__(self, territorio: TerritorioRepository) -> None:
        self._territorio = territorio

    def ejecutar(
        self,
        id_municipio: int,
        datos: ActualizarDisponibilidadMunicipioCreate,
        ahora: datetime | None = None,
    ) -> DisponibilidadMunicipioResponse:
        habilitado = datos.habilitado
        if type(habilitado) is not bool:
            raise DisponibilidadMunicipioInvalidaError()

        try:
            municipio = self._territorio.obtener_municipio(id_municipio)
        except Exception as error:
            raise PersistenciaMunicipioError() from error
        if municipio is None:
            raise MunicipioNoEncontradoError()

        if municipio.habilitado == habilitado:
            return _respuesta(
                municipio,
                "El municipio ya se encontraba en el estado solicitado (sin cambios)",
            )

        fecha_actualizacion = ahora or datetime.now(_ZONA_HORARIA_COLOMBIA)
        if fecha_actualizacion.utcoffset() != _ZONA_HORARIA_COLOMBIA.utcoffset(None):
            fecha_actualizacion = fecha_actualizacion.astimezone(
                _ZONA_HORARIA_COLOMBIA
            )
        try:
            actualizado = self._territorio.actualizar_disponibilidad_municipio(
                id_municipio,
                habilitado,
                fecha_actualizacion,
            )
        except Exception as error:
            raise PersistenciaMunicipioError() from error
        if actualizado is None:
            raise MunicipioNoEncontradoError()
        return _respuesta(
            actualizado,
            "Disponibilidad del municipio actualizada exitosamente",
        )


def _respuesta(
    municipio: MunicipioTerritorial,
    mensaje: str,
) -> DisponibilidadMunicipioResponse:
    return DisponibilidadMunicipioResponse(
        mensaje=mensaje,
        data=DisponibilidadMunicipioData(
            id_municipio=municipio.id_municipio,
            nombre=municipio.nombre,
            id_departamento=municipio.id_departamento,
            habilitado=municipio.habilitado,
            fecha_actualizacion=municipio.fecha_actualizacion.isoformat(),
        ),
    )