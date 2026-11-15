class ParametrosPagoNoDisponiblesError(Exception):
    """No fue posible consultar los parámetros de pagos."""


class UltimoMetodoPagoActivoError(Exception):
    """Se intenta inactivar el último método de pago activo."""
