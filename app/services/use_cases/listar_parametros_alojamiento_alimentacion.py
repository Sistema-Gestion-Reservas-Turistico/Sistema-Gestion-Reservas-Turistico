import sqlite3

from app.domain.exceptions.parametros_alojamiento_alimentacion import (
    ParametrosAlojamientoAlimentacionNoDisponiblesError,
)
from app.domain.exceptions.persistencia import ErrorBaseDatos
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.domain.models.parametros_alojamiento_alimentacion import (
    CategoriaAlojamientoAlimentacionResponse,
    ParametrosAlojamientoAlimentacionResponse,
    RESTRICCION_ALIMENTARIA,
    TIPO_ALIMENTACION,
    TIPO_HABITACION,
    ValorAlojamientoAlimentacionResponse,
)


_CATEGORIAS_ALOJAMIENTO_ALIMENTACION = (
    TIPO_HABITACION,
    TIPO_ALIMENTACION,
    RESTRICCION_ALIMENTARIA,
)


class ListarParametrosAlojamientoAlimentacion:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> ParametrosAlojamientoAlimentacionResponse:
        try:
            categorias = {
                categoria.clave.casefold(): categoria
                for categoria in self._categorias.listar()
            }
            resultado: list[CategoriaAlojamientoAlimentacionResponse] = []
            for clave in _CATEGORIAS_ALOJAMIENTO_ALIMENTACION:
                categoria = categorias.get(clave.casefold())
                if categoria is None:
                    raise ParametrosAlojamientoAlimentacionNoDisponiblesError()
                valores = self._valores.listar(categoria.clave)
                resultado.append(
                    CategoriaAlojamientoAlimentacionResponse(
                        clave=categoria.clave,
                        nombre=categoria.nombre,
                        valores=[
                            ValorAlojamientoAlimentacionResponse(
                                id=valor.id,
                                codigo=valor.codigo,
                                nombre=valor.nombre,
                                orden=valor.orden,
                                activo=valor.activo,
                                es_sistema=valor.es_sistema,
                            )
                            for valor in valores
                        ],
                    )
                )
            return ParametrosAlojamientoAlimentacionResponse(
                categorias=resultado
            )
        except (ErrorBaseDatos, sqlite3.Error) as error:
            raise ParametrosAlojamientoAlimentacionNoDisponiblesError() from error
