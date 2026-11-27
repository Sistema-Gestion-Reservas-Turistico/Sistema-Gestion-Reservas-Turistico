from datetime import datetime, timezone

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.domain.entities.usuario import Usuario
from app.domain.interfaces.usuarios import UsuarioRepository
from app.services.security.passwords import hash_password


class CargarUsuarioAdministrador:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    def ejecutar(self) -> None:
        if not ADMIN_EMAIL or not ADMIN_PASSWORD:
            return
        if self._usuarios.buscar_por_correo(ADMIN_EMAIL) is not None:
            return

        self._usuarios.registrar(
            Usuario(
                id=0,
                tipo_documento="CC",
                numero_documento="ADMIN-BOOTSTRAP",
                nombres="System",
                apellidos="Administrator",
                correo=ADMIN_EMAIL,
                telefono=None,
                password_hash=hash_password(ADMIN_PASSWORD),
                rol="Administrador",
                estado="ACTIVO",
                acepta_tratamiento_datos=True,
                fecha_aceptacion_datos=datetime.now(timezone.utc),
                intentos_fallidos=0,
                bloqueado_hasta=None,
                creado_en=datetime.now(timezone.utc),
            )
        )
