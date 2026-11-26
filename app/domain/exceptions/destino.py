class DestinoNoEncontradoError(Exception):
    def __init__(self) -> None:
        super().__init__("No existe un destino con el identificador indicado")


class CoordenadasFueraDeRangoError(Exception):
    def __init__(self, campo: str) -> None:
        mensajes = {
            "latitud": "La latitud debe estar entre -90 y 90",
            "longitud": "La longitud debe estar entre -180 y 180",
        }
        super().__init__(mensajes[campo])
        self.campo = campo


class CoincidenciaTerritorialError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Las coordenadas indicadas no pertenecen al municipio asociado al destino"
        )


class PersistenciaCoordenadasError(Exception):
    def __init__(self) -> None:
        super().__init__("No fue posible registrar las coordenadas del destino")