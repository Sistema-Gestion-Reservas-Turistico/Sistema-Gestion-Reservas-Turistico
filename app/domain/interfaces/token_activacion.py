from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from app.domain.entities.token_activacion import TokenActivacionCuenta


class TokenActivacionRepository(ABC):
    @abstractmethod
    def guardar(self, token: TokenActivacionCuenta) -> TokenActivacionCuenta:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_token_hash(self, token_hash: str) -> TokenActivacionCuenta | None:
        raise NotImplementedError

    @abstractmethod
    def marcar_como_usado(self, token_id: int, usado_en: datetime) -> bool:
        raise NotImplementedError

    @abstractmethod
    def invalidar_tokens_pendientes(self, usuario_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def registrar_solicitud_reenvio(
        self,
        correo_normalizado: str,
        solicitada_en: datetime,
        maximo: int,
        ventana: timedelta,
    ) -> bool:
        raise NotImplementedError
