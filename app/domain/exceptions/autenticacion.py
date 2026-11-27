from datetime import datetime


class CredencialesInvalidasLoginError(Exception):
    def __init__(self, intentos_restantes: int) -> None:
        super().__init__("Correo o contraseña incorrectos")
        self.intentos_restantes = intentos_restantes


class CuentaBloqueadaTemporalmenteError(Exception):
    def __init__(
        self, bloqueada_hasta: datetime, minutos_restantes: int
    ) -> None:
        super().__init__("La cuenta está bloqueada temporalmente")
        self.bloqueada_hasta = bloqueada_hasta
        self.minutos_restantes = minutos_restantes


class CuentaPendienteActivacionError(Exception):
    def __init__(self) -> None:
        super().__init__("La cuenta aún no ha sido activada")


class PersistenciaSeguridadLoginError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible iniciar sesión")
