class ParametrosEstructuraInvalidosError(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)


class PersistenciaEstructuraTerritorialError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible consultar la estructura territorial")
