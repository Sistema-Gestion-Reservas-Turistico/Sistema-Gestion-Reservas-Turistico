import sqlite3

from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.parametros_pagos import ErrorBaseDatos
from app.domain.exceptions.valores_categorias_domain import (
    CategoriaValorNoEncontradaError,
    ParametroNoVigenteError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class ParametrosConsultaNoDisponiblesError(Exception):
    """No fue posible consultar los parámetros por un error de persistencia."""


class ConsultarParametrosCategoria:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def listar_vigentes(self, clave: str) -> list[ValorCategoriaParametro]:
        try:
            categoria = self._obtener_categoria(clave)
            return self._valores.listar(categoria.clave, activo=True)
        except (ErrorBaseDatos, sqlite3.Error) as error:
            raise ParametrosConsultaNoDisponiblesError() from error

    def obtener_vigente(
        self, clave: str, codigo: str
    ) -> ValorCategoriaParametro:
        try:
            categoria = self._obtener_categoria(clave)
            valor = next(
                (
                    item
                    for item in self._valores.listar(categoria.clave, activo=True)
                    if item.codigo.casefold() == codigo.casefold()
                ),
                None,
            )
        except (ErrorBaseDatos, sqlite3.Error) as error:
            raise ParametrosConsultaNoDisponiblesError() from error
        if valor is None:
            raise ParametroNoVigenteError(codigo)
        return valor

    def _obtener_categoria(self, clave: str):
        categoria = next(
            (
                item
                for item in self._categorias.listar()
                if item.clave.casefold() == clave.casefold()
            ),
            None,
        )
        if categoria is None:
            raise CategoriaValorNoEncontradaError(clave)
        return categoria
