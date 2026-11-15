from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.services.use_cases.consultar_parametros_categoria import (
    ConsultarParametrosCategoria,
)


def obtener_caso_consultar_parametros_categoria() -> ConsultarParametrosCategoria:
    return ConsultarParametrosCategoria(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
    )
