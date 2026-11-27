class CategoriaParametroDuplicadaError(Exception):
    """Se lanza cuando la clave de una categoría ya está registrada."""


class CategoriaParametroNoEncontradaError(Exception):
    """Se lanza cuando no existe la categoría solicitada."""
