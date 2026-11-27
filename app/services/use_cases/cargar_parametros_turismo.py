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
from app.services.use_cases.save_destination import TOURISM_TYPE_CATEGORY


_TOURISM_TYPES = (
    ("AVENTURA", "Adventure"),
    ("ECOTURISMO", "Ecotourism"),
)


class CargarParametrosTurismo:
    def __init__(
        self,
        categories: CategoriaParametroRepository,
        values: ValoresCategoriaRepository,
    ) -> None:
        self._categories = categories
        self._values = values

    def ejecutar(self) -> None:
        category = next(
            (
                item
                for item in self._categories.listar()
                if item.clave.casefold() == TOURISM_TYPE_CATEGORY.casefold()
            ),
            None,
        )
        if category is None:
            try:
                category = self._categories.crear(
                    CategoriaParametro(
                        id=0,
                        clave=TOURISM_TYPE_CATEGORY,
                        nombre="Tourism type",
                        descripcion="Tourism types available for destinations",
                    )
                )
            except CategoriaParametroDuplicadaError:
                category = next(
                    (
                        item
                        for item in self._categories.listar()
                        if item.clave.casefold()
                        == TOURISM_TYPE_CATEGORY.casefold()
                    ),
                    None,
                )
        if category is None:
            return

        existing = {
            item.codigo.casefold(): item
            for item in self._values.listar(category.clave)
        }
        for order, (code, name) in enumerate(_TOURISM_TYPES, 1):
            current = existing.get(code.casefold())
            if current is not None:
                if not current.activo:
                    self._values.actualizar_estado(category.clave, current.id, True)
                continue
            try:
                self._values.crear(
                    categoria=category.clave,
                    codigo=code,
                    nombre=name,
                    descripcion=name,
                    orden=order,
                    es_sistema=True,
                )
            except ValorCategoriaDuplicadoError:
                continue
