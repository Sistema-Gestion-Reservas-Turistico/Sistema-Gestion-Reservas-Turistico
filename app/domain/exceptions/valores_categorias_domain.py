class CategoriaValorNoEncontradaError(Exception):
    """Se lanza cuando no existe la categoría solicitada."""


class ValorCategoriaDuplicadoError(Exception):
    """Se lanza cuando el código ya existe dentro de la categoría."""


class ValorCategoriaNoEncontradoError(Exception):
    """Se lanza cuando no existe el valor solicitado en la categoría."""


class ValorCategoriaSistemaNoInactivableError(Exception):
    """Se lanza cuando se intenta inactivar un valor del sistema."""
