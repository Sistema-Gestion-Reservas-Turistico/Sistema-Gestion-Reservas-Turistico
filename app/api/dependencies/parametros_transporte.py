from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.services.use_cases.cargar_parametros_transporte import (
    CargarParametrosTransporte,
)


def obtener_caso_cargar_parametros_transporte() -> CargarParametrosTransporte:
    return CargarParametrosTransporte(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )