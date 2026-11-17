from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.seguridad_login import (
    EstadoIntentosLogin,
    RegistroSeguridadLogin,
)


class ControlIntentosLoginRepository(ABC):
    @abstractmethod
    def obtener_estado(self, correo_normalizado: str) -> EstadoIntentosLogin | None:
        raise NotImplementedError

    @abstractmethod
    def registrar_intento_fallido(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
        max_intentos: int,
        minutos_bloqueo: int,
    ) -> EstadoIntentosLogin:
        raise NotImplementedError

    @abstractmethod
    def aplicar_bloqueo(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        bloqueado_hasta: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        raise NotImplementedError

    @abstractmethod
    def levantar_bloqueo(
        self, correo_normalizado: str, fecha_hora: datetime
    ) -> EstadoIntentosLogin:
        raise NotImplementedError

    @abstractmethod
    def reiniciar_contador(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        minutos_bloqueo: int,
        ip_origen: str | None = None,
    ) -> EstadoIntentosLogin:
        raise NotImplementedError

    @abstractmethod
    def marcar_notificacion_enviada(self, correo_normalizado: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def registrar_evento(
        self, evento: RegistroSeguridadLogin
    ) -> RegistroSeguridadLogin:
        raise NotImplementedError

    @abstractmethod
    def consultar_eventos(
        self, correo_normalizado: str
    ) -> list[RegistroSeguridadLogin]:
        raise NotImplementedError

    @abstractmethod
    def registrar_login_exitoso(
        self,
        correo_normalizado: str,
        fecha_hora: datetime,
        ip_origen: str | None,
    ) -> EstadoIntentosLogin:
        raise NotImplementedError
