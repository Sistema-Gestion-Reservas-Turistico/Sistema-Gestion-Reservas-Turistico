import hashlib
from datetime import datetime, timezone

from app.domain.exceptions.activacion import (
    CuentaYaActivaError,
    PersistenciaActivacionError,
    TokenActivacionInvalidoError,
    TokenActivacionVencidoError,
)
from app.domain.interfaces.token_activacion import TokenActivacionRepository
from app.domain.interfaces.usuarios import UsuarioRepository
from app.domain.models.activacion import ActivarCuentaResponse, ActivarCuentaRequest


class ActivarCuentaPorTokenUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        tokens: TokenActivacionRepository,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens

    def ejecutar(self, solicitud: ActivarCuentaRequest) -> ActivarCuentaResponse:
        token_hash = hashlib.sha256(solicitud.token.encode("utf-8")).hexdigest()
        try:
            token = self._tokens.buscar_por_token_hash(token_hash)
        except Exception as error:
            raise PersistenciaActivacionError() from error

        if token is None or token.invalidado:
            raise TokenActivacionInvalidoError()
        if token.usado:
            raise CuentaYaActivaError()

        try:
            usuario = self._usuarios.buscar_por_id(token.usuario_id)
        except Exception as error:
            raise PersistenciaActivacionError() from error
        if usuario is None:
            raise TokenActivacionInvalidoError()
        if usuario.estado == "ACTIVA":
            raise CuentaYaActivaError()

        ahora = datetime.now(timezone.utc)
        if ahora >= token.expira_en:
            raise TokenActivacionVencidoError()

        try:
            consumido = self._tokens.marcar_como_usado(token.id, ahora)
            if not consumido:
                estado_actual = self._tokens.buscar_por_token_hash(token_hash)
                if estado_actual is None or estado_actual.invalidado:
                    raise TokenActivacionInvalidoError()
                if estado_actual.usado:
                    raise CuentaYaActivaError()
                raise RuntimeError("No fue posible consumir el token")
            usuario_activado = self._usuarios.activar(usuario.id, ahora)
        except (CuentaYaActivaError, TokenActivacionInvalidoError):
            raise
        except Exception as error:
            raise PersistenciaActivacionError() from error

        if usuario_activado is None:
            raise TokenActivacionInvalidoError()
        return ActivarCuentaResponse(
            id=usuario_activado.id,
            correo=usuario_activado.correo,
            estado=usuario_activado.estado,
            fecha_activacion=ahora,
        )
