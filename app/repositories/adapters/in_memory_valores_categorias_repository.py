from threading import RLock

from app.domain.entities.valor_categoria_parametro import ValorCategoriaParametro
from app.domain.exceptions.valores_categorias_domain import (
    ValorCategoriaDuplicadoError,
    ValorCategoriaNoEncontradoError,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository


class InMemoryValoresCategoriaRepository(ValoresCategoriaRepository):
    def __init__(self) -> None:
        self._valores: dict[int, ValorCategoriaParametro] = {}
        self._siguiente_id = 1
        self._lock = RLock()

    def listar(
        self, categoria: str, activo: bool | None = None
    ) -> list[ValorCategoriaParametro]:
        with self._lock:
            valores = [
                valor
                for valor in self._valores.values()
                if valor.categoria.casefold() == categoria.casefold()
                and (activo is None or valor.activo is activo)
            ]
            return sorted(valores, key=lambda valor: (valor.orden, valor.id))

    def crear(
        self,
        categoria: str,
        codigo: str,
        nombre: str,
        descripcion: str,
        orden: int | None,
    ) -> ValorCategoriaParametro:
        with self._lock:
            if any(
                valor.categoria.casefold() == categoria.casefold()
                and valor.codigo.casefold() == codigo.casefold()
                for valor in self._valores.values()
            ):
                raise ValorCategoriaDuplicadoError(codigo)

            valores_categoria = [
                valor
                for valor in self._valores.values()
                if valor.categoria.casefold() == categoria.casefold()
            ]
            nuevo_orden = (
                orden
                if orden is not None
                else max((valor.orden for valor in valores_categoria), default=0) + 1
            )
            valor = ValorCategoriaParametro(
                id=self._siguiente_id,
                categoria=categoria,
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                orden=nuevo_orden,
                activo=True,
            )
            self._valores[valor.id] = valor
            self._siguiente_id += 1
            return valor

    def actualizar(
        self,
        categoria: str,
        valor_id: int,
        nombre: str | None,
        descripcion: str | None,
        orden: int | None,
    ) -> ValorCategoriaParametro:
        with self._lock:
            valor = self._valores.get(valor_id)
            if valor is None or valor.categoria.casefold() != categoria.casefold():
                raise ValorCategoriaNoEncontradoError(valor_id)

            valor_actualizado = ValorCategoriaParametro(
                id=valor.id,
                categoria=valor.categoria,
                codigo=valor.codigo,
                nombre=nombre if nombre is not None else valor.nombre,
                descripcion=(
                    descripcion if descripcion is not None else valor.descripcion
                ),
                orden=orden if orden is not None else valor.orden,
                activo=valor.activo,
            )
            self._valores[valor_id] = valor_actualizado
            return valor_actualizado

    def actualizar_estado(
        self, categoria: str, valor_id: int, activo: bool
    ) -> ValorCategoriaParametro:
        with self._lock:
            valor = self._valores.get(valor_id)
            if valor is None or valor.categoria.casefold() != categoria.casefold():
                raise ValorCategoriaNoEncontradoError(valor_id)

            valor_actualizado = ValorCategoriaParametro(
                id=valor.id,
                categoria=valor.categoria,
                codigo=valor.codigo,
                nombre=valor.nombre,
                descripcion=valor.descripcion,
                orden=valor.orden,
                activo=activo,
            )
            self._valores[valor_id] = valor_actualizado
            return valor_actualizado
