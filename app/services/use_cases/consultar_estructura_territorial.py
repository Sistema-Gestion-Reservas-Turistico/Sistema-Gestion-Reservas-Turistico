from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import MunicipioTerritorial
from app.domain.exceptions.estructura_territorial import (
    ParametrosEstructuraInvalidosError,
    PersistenciaEstructuraTerritorialError,
)
from app.domain.interfaces.territorio import TerritorioRepository
from app.domain.models.estructura_territorial import (
    DepartamentoEstructuraItem,
    EstructuraTerritorialData,
    EstructuraTerritorialResponse,
    MunicipioEstructuraItem,
)


class ConsultarEstructuraTerritorialUseCase:
    _ERROR_PAIS = (
        "El identificador del país es obligatorio y debe ser numérico"
    )
    _ERROR_DEPARTAMENTO = (
        "El identificador del departamento debe ser numérico"
    )

    def __init__(self, territorio: TerritorioRepository) -> None:
        self._territorio = territorio

    def ejecutar(
        self,
        id_pais: int | str | None,
        id_departamento: int | str | None = None,
    ) -> EstructuraTerritorialResponse:
        pais_id = self._validar_identificador(id_pais, self._ERROR_PAIS)
        departamento_id = (
            self._validar_identificador(
                id_departamento, self._ERROR_DEPARTAMENTO
            )
            if id_departamento is not None
            else None
        )

        try:
            pais, departamentos = self._territorio.consultar_estructura_territorial(
                pais_id, departamento_id
            )
            if pais is None or not departamentos:
                return EstructuraTerritorialResponse(
                    mensaje="No existe estructura territorial para el país indicado",
                    data=EstructuraTerritorialData(
                        id_pais=pais_id,
                        total_departamentos=0,
                        total_municipios=0,
                        departamentos=[],
                    ),
                    success=False,
                )

            departamentos_data = [
                self._mapear_departamento(departamento, municipios)
                for departamento, municipios in departamentos
            ]
            total_municipios = sum(
                len(departamento.municipios)
                for departamento in departamentos_data
            )
            return EstructuraTerritorialResponse(
                mensaje="Consulta de estructura territorial exitosa",
                data=EstructuraTerritorialData(
                    id_pais=pais_id,
                    nombre=pais.nombre,
                    total_departamentos=len(departamentos_data),
                    total_municipios=total_municipios,
                    departamentos=departamentos_data,
                ),
                success=True,
            )
        except Exception as error:
            raise PersistenciaEstructuraTerritorialError() from error

    @staticmethod
    def _validar_identificador(
        valor: int | str | None, mensaje_error: str
    ) -> int:
        if (
            isinstance(valor, bool)
            or valor is None
            or not isinstance(valor, (int, str))
        ):
            raise ParametrosEstructuraInvalidosError(mensaje_error)
        try:
            identificador = int(valor)
        except (TypeError, ValueError) as error:
            raise ParametrosEstructuraInvalidosError(mensaje_error) from error
        if identificador <= 0:
            raise ParametrosEstructuraInvalidosError(mensaje_error)
        return identificador

    @staticmethod
    def _mapear_departamento(
        departamento: Departamento,
        municipios: list[MunicipioTerritorial],
    ) -> DepartamentoEstructuraItem:
        return DepartamentoEstructuraItem(
            id=departamento.id,
            nombre=departamento.nombre,
            municipios=[
                MunicipioEstructuraItem(
                    id=municipio.id_municipio,
                    nombre=municipio.nombre,
                    habilitado=municipio.habilitado,
                )
                for municipio in municipios
            ],
        )
