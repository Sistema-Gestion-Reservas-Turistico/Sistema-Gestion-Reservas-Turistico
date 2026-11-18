from dataclasses import replace
from datetime import datetime, timedelta
from threading import Lock

from app.domain.entities.token_activacion import TokenActivacionCuenta
from app.domain.interfaces.token_activacion import TokenActivacionRepository


class InMemoryTokenActivacionRepository(TokenActivacionRepository):
    def __init__(self) -> None:
        self._tokens: dict[int, TokenActivacionCuenta] = {}
        self._solicitudes_reenvio: dict[str, list[datetime]] = {}
        self._siguiente_id = 1
        self._lock = Lock()

    def guardar(self, token: TokenActivacionCuenta) -> TokenActivacionCuenta:
        with self._lock:
            for token_id, existente in self._tokens.items():
                if (
                    existente.usuario_id == token.usuario_id
                    and not existente.usado
                    and not existente.invalidado
                ):
                    self._tokens[token_id] = replace(existente, invalidado=True)

            guardado = replace(token, id=self._siguiente_id)
            self._tokens[guardado.id] = guardado
            self._siguiente_id += 1
            return guardado

    def buscar_por_token_hash(self, token_hash: str) -> TokenActivacionCuenta | None:
        with self._lock:
            return next(
                (
                    token
                    for token in self._tokens.values()
                    if token.token_hash == token_hash
                ),
                None,
            )

    def marcar_como_usado(self, token_id: int, usado_en: datetime) -> bool:
        with self._lock:
            token = self._tokens.get(token_id)
            if token is None or token.usado or token.invalidado:
                return False
            self._tokens[token_id] = replace(
                token, usado=True, usado_en=usado_en
            )
            return True

    def invalidar_tokens_pendientes(self, usuario_id: int) -> None:
        with self._lock:
            for token_id, token in self._tokens.items():
                if (
                    token.usuario_id == usuario_id
                    and not token.usado
                    and not token.invalidado
                ):
                    self._tokens[token_id] = replace(token, invalidado=True)

    def registrar_solicitud_reenvio(
        self,
        correo_normalizado: str,
        solicitada_en: datetime,
        maximo: int,
        ventana: timedelta,
    ) -> bool:
        with self._lock:
            cutoff = solicitada_en - ventana
            recientes = [
                fecha
                for fecha in self._solicitudes_reenvio.get(correo_normalizado, [])
                if fecha > cutoff
            ]
            if len(recientes) >= maximo:
                self._solicitudes_reenvio[correo_normalizado] = recientes
                return False
            recientes.append(solicitada_en)
            self._solicitudes_reenvio[correo_normalizado] = recientes
            return True
