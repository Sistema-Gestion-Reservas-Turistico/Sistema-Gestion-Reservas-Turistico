from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
)
from app.domain.exceptions.valores_categorias_domain import (
    ValorCategoriaDuplicadoError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.domain.models.parametros_pagos import (
    CategoriaParametroPagoCreate,
    ESTADO_TRANSACCION,
    METODO_PAGO,
    ValorParametroPagoCreate,
)


_PARAMETROS_INICIALES = (
    (
        CategoriaParametroPagoCreate(
            clave=METODO_PAGO,
            nombre="Método de pago",
            descripcion="Métodos de pago disponibles",
        ),
        (
            ValorParametroPagoCreate(
                codigo="TARJETA_CREDITO",
                nombre="Tarjeta de crédito",
                descripcion="Tarjeta de crédito",
                orden=1,
                es_sistema=False,
            ),
        ),
    ),
    (
        CategoriaParametroPagoCreate(
            clave=ESTADO_TRANSACCION,
            nombre="Estado de transacción",
            descripcion="Estados de las transacciones de pago",
        ),
        (
            ValorParametroPagoCreate(
                codigo="PENDIENTE",
                nombre="Pendiente",
                descripcion="Pendiente",
                orden=1,
                es_sistema=True,
            ),
            ValorParametroPagoCreate(
                codigo="APROBADA",
                nombre="Aprobada",
                descripcion="Aprobada",
                orden=2,
                es_sistema=True,
            ),
            ValorParametroPagoCreate(
                codigo="RECHAZADA",
                nombre="Rechazada",
                descripcion="Rechazada",
                orden=3,
                es_sistema=True,
            ),
        ),
    ),
)


class CargarParametrosPagos:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> None:
        for datos_categoria, valores_iniciales in _PARAMETROS_INICIALES:
            categoria = next(
                (
                    item
                    for item in self._categorias.listar()
                    if item.clave.casefold() == datos_categoria.clave.casefold()
                ),
                None,
            )
            if categoria is None:
                try:
                    categoria = self._categorias.crear(
                        CategoriaParametro(
                            id=0,
                            clave=datos_categoria.clave,
                            nombre=datos_categoria.nombre,
                            descripcion=datos_categoria.descripcion,
                        )
                    )
                except CategoriaParametroDuplicadaError:
                    categoria = next(
                        (
                            item
                            for item in self._categorias.listar()
                            if item.clave.casefold()
                            == datos_categoria.clave.casefold()
                        ),
                        None,
                    )
            if categoria is None:
                continue

            codigos_existentes = {
                valor.codigo.casefold()
                for valor in self._valores.listar(categoria.clave)
            }
            for valor_inicial in valores_iniciales:
                if valor_inicial.codigo.casefold() in codigos_existentes:
                    continue
                try:
                    self._valores.crear(
                        categoria=categoria.clave,
                        codigo=valor_inicial.codigo,
                        nombre=valor_inicial.nombre,
                        descripcion=valor_inicial.descripcion,
                        orden=valor_inicial.orden,
                        es_sistema=valor_inicial.es_sistema,
                    )
                except ValorCategoriaDuplicadoError:
                    continue
                codigos_existentes.add(valor_inicial.codigo.casefold())
