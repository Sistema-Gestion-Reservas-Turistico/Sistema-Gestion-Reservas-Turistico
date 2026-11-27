class TokenActivacionInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El enlace de activación no es válido")


class CuentaYaActivaError(Exception):
    def __init__(self) -> None:
        super().__init__("La cuenta ya está activa")


class TokenActivacionVencidoError(Exception):
    def __init__(self) -> None:
        super().__init__("El enlace de activación venció. Solicita uno nuevo")


class LimiteReenviosActivacionError(Exception):
    def __init__(self) -> None:
        super().__init__("Demasiadas solicitudes. Intenta de nuevo más tarde")


class PersistenciaActivacionError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible procesar la activación")
