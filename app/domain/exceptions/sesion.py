class SesionCerradaPorInactividadError(Exception):
    codigo = "SESION_INACTIVA"

    def __init__(self) -> None:
        super().__init__("Tu sesión se cerró por inactividad. Inicia sesión de nuevo")


class SesionInvalidaOCerradaError(Exception):
    def __init__(self) -> None:
        super().__init__("La sesión es inválida, venció o ya fue cerrada")


class PersistenciaSesionError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible validar la sesión")