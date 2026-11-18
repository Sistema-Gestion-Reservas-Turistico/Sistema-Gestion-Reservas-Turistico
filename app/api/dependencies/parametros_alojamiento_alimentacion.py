from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.services.use_cases.cargar_parametros_alojamiento_alimentacion import (
    CargarParametrosAlojamientoAlimentacion,
)
from app.services.use_cases.listar_parametros_alojamiento_alimentacion import (
    ListarParametrosAlojamientoAlimentacion,
)


def obtener_caso_listar_parametros_alojamiento_alimentacion(
) -> ListarParametrosAlojamientoAlimentacion:
    return ListarParametrosAlojamientoAlimentacion(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )


@lru_cache
def obtener_caso_cargar_parametros_alojamiento_alimentacion(
) -> CargarParametrosAlojamientoAlimentacion:
    return CargarParametrosAlojamientoAlimentacion(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )
