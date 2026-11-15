from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    ValorCategoriaNoEncontradoError,
    ValorCategoriaSistemaNoInactivableError,
)
from app.domain.exceptions.parametros_pagos import UltimoMetodoPagoActivoError
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.domain.models.parametros_pagos import METODO_PAGO


class ActualizarEstadoValorCategoriaParametro:
    def __init__(self, repositorio: ValoresCategoriaRepository) -> None:
        self._repositorio = repositorio

    def ejecutar(
        self, categoria: str, valor_id: int, activo: bool
    ) -> ValorCategoriaParametro:
        valor = next(
            (
                item
                for item in self._repositorio.listar(categoria)
                if item.id == valor_id
            ),
            None,
        )
        if valor is None:
            raise ValorCategoriaNoEncontradoError(valor_id)
        if not activo and valor.es_sistema:
            raise ValorCategoriaSistemaNoInactivableError(valor_id)
        if (
            not activo
            and valor.activo
            and categoria.casefold() == METODO_PAGO.casefold()
            and self._repositorio.contar_activos(categoria) <= 1
        ):
            raise UltimoMetodoPagoActivoError(valor_id)
        return self._repositorio.actualizar_estado(categoria, valor_id, activo)
