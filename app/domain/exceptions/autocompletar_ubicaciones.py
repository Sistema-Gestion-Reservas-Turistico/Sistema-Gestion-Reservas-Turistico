class ConsultaAutocompletarInvalidaError(Exception):
    def __init__(self, mensaje: str | None = None) -> None:
        super().__init__(
            mensaje or "El texto de búsqueda debe tener al menos 3 caracteres"
        )


class PersistenciaAutocompletarError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible consultar las sugerencias de ubicación")