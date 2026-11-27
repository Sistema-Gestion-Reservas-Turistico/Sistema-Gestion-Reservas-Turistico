class ParametrosUbicacionInvalidosError(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)


class PersistenciaUbicacionesError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible consultar las ubicaciones")