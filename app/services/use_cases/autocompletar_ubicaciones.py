import unicodedata

from app.domain.entities.sugerencia_territorial import SugerenciaTerritorial
from app.domain.exceptions.autocompletar_ubicaciones import (
    ConsultaAutocompletarInvalidaError,
    PersistenciaAutocompletarError,
)
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.autocompletar_ubicaciones import (
    AutocompletarUbicacionesData,
    AutocompletarUbicacionesResponse,
    SugerenciaUbicacionItem,
)


_MENSAJE_CONSULTA_INVALIDA = (
    "El texto de búsqueda debe tener al menos 3 caracteres"
)


class AutocompletarUbicacionesUseCase:
    def __init__(self, territorio: TerritorioRepository) -> None:
        self._territorio = territorio

    def ejecutar(
        self,
        q: str | None,
        limite: int = 10,
    ) -> AutocompletarUbicacionesResponse:
        if not isinstance(q, str) or len(q.strip()) < 3:
            raise ConsultaAutocompletarInvalidaError(
                _MENSAJE_CONSULTA_INVALIDA
            )
        if not isinstance(limite, int) or isinstance(limite, bool) or limite <= 0:
            raise ConsultaAutocompletarInvalidaError(
                "El límite debe ser un entero positivo"
            )

        consulta_normalizada = _normalizar(q.strip())
        try:
            territorios = self._territorio.listar_ubicaciones_autocompletar()
        except Exception as error:
            raise PersistenciaAutocompletarError() from error

        coincidencias = [
            sugerencia
            for sugerencia in territorios
            if consulta_normalizada in _normalizar(sugerencia.nombre)
        ]
        coincidencias.sort(key=lambda item: _clave_orden(item, consulta_normalizada))
        seleccionadas = coincidencias[:limite]
        sugerencias = [
            SugerenciaUbicacionItem(
                id=item.id,
                nombre=item.nombre,
                tipo=item.tipo,
                departamento=item.departamento,
            )
            for item in seleccionadas
        ]
        total = len(sugerencias)
        if total:
            return AutocompletarUbicacionesResponse(
                mensaje="Sugerencias de ubicación encontradas",
                data=AutocompletarUbicacionesData(q, total, sugerencias),
                success=True,
            )
        return AutocompletarUbicacionesResponse(
            mensaje=(
                "No se encontraron ubicaciones que coincidan con el texto ingresado"
            ),
            data=AutocompletarUbicacionesData(q, 0, []),
            success=False,
        )


def _normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto)
    return "".join(
        caracter
        for caracter in descompuesto
        if unicodedata.category(caracter) != "Mn"
    ).lower()


def _clave_orden(
    sugerencia: SugerenciaTerritorial,
    consulta: str,
) -> tuple[int, str]:
    nombre = _normalizar(sugerencia.nombre)
    return (0 if nombre.startswith(consulta) else 1, nombre)