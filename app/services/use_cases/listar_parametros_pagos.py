import sqlite3

from app.domain.exceptions.parametros_pagos import (
    ErrorBaseDatos,
    ParametrosPagoNoDisponiblesError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.domain.models.parametros_pagos import (
    CategoriaParametroPagoResponse,
    ESTADO_TRANSACCION,
    METODO_PAGO,
    ParametrosPagoResponse,
    ValorParametroPagoResponse,
)


_CATEGORIAS_PAGO = (METODO_PAGO, ESTADO_TRANSACCION)


class ListarParametrosPagos:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> ParametrosPagoResponse:
        try:
            categorias = {
                categoria.clave.casefold(): categoria
                for categoria in self._categorias.listar()
            }
            resultado: list[CategoriaParametroPagoResponse] = []
            for clave in _CATEGORIAS_PAGO:
                categoria = categorias.get(clave.casefold())
                if categoria is None:
                    raise ParametrosPagoNoDisponiblesError()
                valores = self._valores.listar(categoria.clave)
                resultado.append(
                    CategoriaParametroPagoResponse(
                        clave=categoria.clave,
                        nombre=categoria.nombre,
                        valores=[
                            ValorParametroPagoResponse(
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
            return ParametrosPagoResponse(categorias=resultado)
        except (ErrorBaseDatos, sqlite3.Error) as error:
            raise ParametrosPagoNoDisponiblesError() from error
