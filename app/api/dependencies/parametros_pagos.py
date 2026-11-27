from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.services.use_cases.cargar_parametros_pagos import CargarParametrosPagos
from app.services.use_cases.listar_parametros_pagos import ListarParametrosPagos


def obtener_caso_listar_parametros_pagos() -> ListarParametrosPagos:
    return ListarParametrosPagos(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )


@lru_cache
def obtener_caso_cargar_parametros_pagos() -> CargarParametrosPagos:
    return CargarParametrosPagos(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )
