from app.domain.models.usuarios import ErrorCampoItem


class CorreoDuplicadoError(Exception):
    """El correo ya está asociado a una cuenta."""


class DocumentoDuplicadoError(Exception):
    """El documento ya está asociado a una cuenta."""


class DatosRegistroInvalidosError(Exception):
    def __init__(self, errores: list[ErrorCampoItem]) -> None:
        super().__init__("Los datos de registro no son válidos")
        self.errores = errores


class TratamientoDatosNoAceptadoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Debes aceptar el tratamiento de datos personales para registrarte"
        )


class PersistenciaUsuariosError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible completar el registro")
