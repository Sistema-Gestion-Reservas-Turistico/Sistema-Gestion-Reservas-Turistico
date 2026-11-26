from dataclasses import dataclass

from app.domain.entities.destino import Destino


@dataclass(frozen=True)
class RegistrarCoordenadasDestinoCreate:
    latitud: float
    longitud: float


@dataclass(frozen=True)
class CoordenadasDestinoData:
    id_destino: int
    nombre: str
    id_municipio: int
    latitud: float
    longitud: float
    estado_coordenadas: str


@dataclass(frozen=True)
class RegistrarCoordenadasDestinoResponse:
    mensaje: str
    data: CoordenadasDestinoData
    success: bool = True

    @classmethod
    def desde_destino(cls, destino: Destino) -> "RegistrarCoordenadasDestinoResponse":
        if destino.latitud is None or destino.longitud is None:
            raise ValueError("El destino no tiene coordenadas registradas")
        return cls(
            mensaje="Coordenadas del destino registradas exitosamente",
            data=CoordenadasDestinoData(
                id_destino=destino.id_destino,
                nombre=destino.nombre,
                id_municipio=destino.id_municipio,
                latitud=destino.latitud,
                longitud=destino.longitud,
                estado_coordenadas=destino.estado_coordenadas,
            ),
        )