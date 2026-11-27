import logging
import re
from datetime import datetime, timezone

from app.domain.entities.usuario import Usuario
from app.domain.exceptions.usuarios import (
    CorreoDuplicadoError,
    DatosRegistroInvalidosError,
    DocumentoDuplicadoError,
    PersistenciaUsuariosError,
    TratamientoDatosNoAceptadoError,
)
from app.domain.interfaces.usuarios import UsuarioRepository
from app.domain.interfaces.notificacion_correo import NotificacionCorreoService
from app.domain.interfaces.token_activacion import TokenActivacionRepository
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.domain.models.usuarios import (
    ESTADO_PENDIENTE_ACTIVACION,
    ROL_CLIENTE,
    TIPO_DOCUMENTO,
    ErrorCampoItem,
    UsuarioRegistroCreate,
    UsuarioRegistroResponse,
)
from app.services.security.passwords import hash_password
from app.services.use_cases.activacion_utils import crear_y_enviar_token_activacion


_EMAIL_RE: re.Pattern[str] = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)
_logger = logging.getLogger(__name__)


class RegistrarUsuarioUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        valores_categoria: ValoresCategoriaRepository,
        tokens_activacion: TokenActivacionRepository,
        notificaciones: NotificacionCorreoService,
    ) -> None:
        self._usuarios = usuarios
        self._valores_categoria = valores_categoria
        self._tokens_activacion = tokens_activacion
        self._notificaciones = notificaciones

    def ejecutar(self, datos: UsuarioRegistroCreate) -> UsuarioRegistroResponse:
        if datos.acepta_tratamiento_datos is not True:
            raise TratamientoDatosNoAceptadoError()

        errores = self._validar_datos(datos)
        if errores:
            raise DatosRegistroInvalidosError(errores)

        try:
            tipos_documento = self._valores_categoria.listar_activos(TIPO_DOCUMENTO)
        except Exception as error:
            raise PersistenciaUsuariosError() from error

        tipo_documento = next(
            (
                valor.codigo
                for valor in tipos_documento
                if valor.codigo.casefold() == datos.tipo_documento.strip().casefold()
            ),
            None,
        )
        if tipo_documento is None:
            raise DatosRegistroInvalidosError(
                [
                    ErrorCampoItem(
                        campo="tipo_documento",
                        detalle="El tipo de documento no es válido o no está vigente",
                    )
                ]
            )

        ahora = datetime.now(timezone.utc)
        correo_normalizado = datos.correo.strip().casefold()
        usuario = Usuario(
            id=0,
            tipo_documento=tipo_documento,
            numero_documento=datos.numero_documento.strip(),
            nombres=datos.nombres.strip(),
            apellidos=datos.apellidos.strip(),
            correo=correo_normalizado,
            telefono=datos.telefono.strip() if datos.telefono else None,
            password_hash=hash_password(datos.password),
            rol=ROL_CLIENTE,
            estado=ESTADO_PENDIENTE_ACTIVACION,
            acepta_tratamiento_datos=True,
            fecha_aceptacion_datos=ahora,
            intentos_fallidos=0,
            bloqueado_hasta=None,
            creado_en=ahora,
        )

        try:
            usuario_guardado = self._usuarios.registrar(usuario)
        except (CorreoDuplicadoError, DocumentoDuplicadoError):
            raise
        except Exception as error:
            raise PersistenciaUsuariosError() from error

        try:
            crear_y_enviar_token_activacion(
                usuario_guardado,
                self._tokens_activacion,
                self._notificaciones,
                ahora,
            )
        except Exception as error:
            _logger.exception(
                "No fue posible preparar la activación de la cuenta %s",
                usuario_guardado.correo,
            )
            raise PersistenciaUsuariosError() from error

        return UsuarioRegistroResponse(
            id=usuario_guardado.id,
            nombres=usuario_guardado.nombres,
            apellidos=usuario_guardado.apellidos,
            correo=usuario_guardado.correo,
            estado=usuario_guardado.estado,
        )

    @staticmethod
    def _validar_datos(datos: UsuarioRegistroCreate) -> list[ErrorCampoItem]:
        errores: list[ErrorCampoItem] = []
        campos_obligatorios = (
            ("tipo_documento", datos.tipo_documento),
            ("numero_documento", datos.numero_documento),
            ("nombres", datos.nombres),
            ("apellidos", datos.apellidos),
            ("correo", datos.correo),
            ("password", datos.password),
        )
        for campo, valor in campos_obligatorios:
            if not isinstance(valor, str) or not valor.strip():
                errores.append(
                    ErrorCampoItem(campo=campo, detalle="Este campo es obligatorio")
                )

        numero_documento = (
            datos.numero_documento.strip()
            if isinstance(datos.numero_documento, str)
            else ""
        )
        if numero_documento and (
            len(numero_documento) > 20 or not numero_documento.isalnum()
        ):
            errores.append(
                ErrorCampoItem(
                    campo="numero_documento",
                    detalle="Debe contener solo caracteres alfanuméricos y máximo 20 caracteres",
                )
            )

        correo = datos.correo.strip() if isinstance(datos.correo, str) else ""
        if correo and (
            not _EMAIL_RE.fullmatch(correo)
            or correo.startswith(".")
            or ".." in correo.split("@", maxsplit=1)[0]
        ):
            errores.append(
                ErrorCampoItem(campo="correo", detalle="Debe ser un correo válido")
            )

        password = datos.password if isinstance(datos.password, str) else ""
        if password and (
            len(password) < 8
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"\d", password)
        ):
            errores.append(
                ErrorCampoItem(
                    campo="password",
                    detalle=(
                        "Debe tener mínimo 8 caracteres, una mayúscula, "
                        "una minúscula y un número"
                    ),
                )
            )
        return errores
