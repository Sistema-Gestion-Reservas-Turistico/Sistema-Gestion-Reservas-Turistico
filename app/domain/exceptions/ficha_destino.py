class IdentificadorDestinoInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El identificador del destino no es válido")


class DestinoActivoNoEncontradoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No existe un destino activo con el identificador indicado"
        )


class PersistenciaFichaDestinoError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible consultar la ficha del destino")
