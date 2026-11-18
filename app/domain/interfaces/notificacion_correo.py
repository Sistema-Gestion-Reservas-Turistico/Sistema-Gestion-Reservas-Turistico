from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.entities.usuario import Usuario


class NotificacionCorreoService(ABC):
    @abstractmethod
    def enviar_aviso_bloqueo_cuenta(
        self,
        usuario: Usuario,
        fecha_hora_bloqueo: datetime,
        bloqueada_hasta: datetime,
    ) -> None:
        raise NotImplementedError
