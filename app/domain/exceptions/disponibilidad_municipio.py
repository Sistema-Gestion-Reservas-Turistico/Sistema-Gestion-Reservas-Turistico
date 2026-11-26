class MunicipioNoEncontradoError(Exception):
    def __init__(self) -> None:
        super().__init__("No existe un municipio con el identificador indicado")


class DisponibilidadMunicipioInvalidaError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "El campo habilitado es obligatorio y debe ser verdadero o falso"
        )


class PersistenciaMunicipioError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No fue posible actualizar la disponibilidad del municipio"
        )