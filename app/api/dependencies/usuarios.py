from functools import lru_cache

from app.api.dependencies.categorias_parametros import (
    obtener_repositorio_categoria_parametro,
)
from app.api.dependencies.valores_categorias_api import (
    obtener_repositorio_valores_categoria,
)
from app.repositories.adapters.in_memory_usuario_repository import (
    InMemoryUsuarioRepository,
)
from app.repositories.adapters.in_memory_control_intentos_login_repository import (
    InMemoryControlIntentosLoginRepository,
)
from app.repositories.adapters.in_memory_notificacion_correo_service import (
    InMemoryNotificacionCorreoService,
)
from app.services.use_cases.autenticar_usuario_con_bloqueo import (
    AutenticarUsuarioConBloqueoUseCase,
)
from app.services.use_cases.cargar_parametros_usuarios import CargarParametrosUsuarios
from app.services.use_cases.registrar_usuario import RegistrarUsuarioUseCase


@lru_cache
def obtener_repositorio_usuarios() -> InMemoryUsuarioRepository:
    return InMemoryUsuarioRepository()


def obtener_caso_registrar_usuario() -> RegistrarUsuarioUseCase:
    return RegistrarUsuarioUseCase(
        obtener_repositorio_usuarios(),
        obtener_repositorio_valores_categoria(),
    )


def obtener_caso_cargar_parametros_usuarios() -> CargarParametrosUsuarios:
    return CargarParametrosUsuarios(
        obtener_repositorio_categoria_parametro(),
        obtener_repositorio_valores_categoria(),
        obtener_repositorio_usuarios(),
    )


@lru_cache
def obtener_repositorio_control_intentos_login() -> (
    InMemoryControlIntentosLoginRepository
):
    return InMemoryControlIntentosLoginRepository()


@lru_cache
def obtener_servicio_notificacion_correo() -> InMemoryNotificacionCorreoService:
    return InMemoryNotificacionCorreoService()


def obtener_caso_autenticar_usuario() -> AutenticarUsuarioConBloqueoUseCase:
    return AutenticarUsuarioConBloqueoUseCase(
        obtener_repositorio_usuarios(),
        obtener_repositorio_control_intentos_login(),
        obtener_servicio_notificacion_correo(),
    )
