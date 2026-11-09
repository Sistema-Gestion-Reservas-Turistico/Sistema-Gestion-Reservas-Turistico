from threading import RLock

from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
    CategoriaParametroNoEncontradaError,
)
from app.domain.interfaces.categorias_parametros_repository import (
    CategoriaParametroRepository,
)


class InMemoryCategoriaParametroRepository(CategoriaParametroRepository):
    def __init__(self) -> None:
        self._categorias: dict[int, CategoriaParametro] = {}
        self._siguiente_id = 1
        self._lock = RLock()

    def crear(self, categoria: CategoriaParametro) -> CategoriaParametro:
        with self._lock:
            self._validar_clave_unica(categoria)
            categoria_guardada = CategoriaParametro(
                id=self._siguiente_id,
                clave=categoria.clave,
                nombre=categoria.nombre,
                descripcion=categoria.descripcion,
            )
            self._categorias[categoria_guardada.id] = categoria_guardada
            self._siguiente_id += 1
            return categoria_guardada

    def listar(self) -> list[CategoriaParametro]:
        with self._lock:
            return list(self._categorias.values())

    def obtener_por_id(self, categoria_id: int) -> CategoriaParametro | None:
        with self._lock:
            return self._categorias.get(categoria_id)

    def actualizar(
        self, categoria_id: int, nombre: str | None, descripcion: str | None
    ) -> CategoriaParametro:
        with self._lock:
            categoria = self._categorias.get(categoria_id)
            if categoria is None:
                raise CategoriaParametroNoEncontradaError(categoria_id)

            categoria_actualizada = CategoriaParametro(
                id=categoria.id,
                clave=categoria.clave,
                nombre=nombre if nombre is not None else categoria.nombre,
                descripcion=(
                    descripcion if descripcion is not None else categoria.descripcion
                ),
            )
            self._categorias[categoria_id] = categoria_actualizada
            return categoria_actualizada

    def _validar_clave_unica(self, categoria: CategoriaParametro) -> None:
        if any(
            existente.clave.casefold() == categoria.clave.casefold()
            for existente in self._categorias.values()
        ):
            raise CategoriaParametroDuplicadaError(categoria.clave)
