from dataclasses import replace
from datetime import datetime
from threading import Lock

from app.domain.entities.usuario import Usuario
from app.domain.exceptions.usuarios import (
    CorreoDuplicadoError,
    DocumentoDuplicadoError,
)
from app.domain.interfaces.usuarios import UsuarioRepository


class InMemoryUsuarioRepository(UsuarioRepository):
    def __init__(self) -> None:
        self._usuarios: dict[int, Usuario] = {}
        self._siguiente_id = 1
        self._lock = Lock()

    def registrar(self, usuario: Usuario) -> Usuario:
        with self._lock:
            correo_normalizado = usuario.correo.casefold()
            if any(
                existente.correo.casefold() == correo_normalizado
                for existente in self._usuarios.values()
            ):
                raise CorreoDuplicadoError()

            if any(
                existente.tipo_documento == usuario.tipo_documento
                and existente.numero_documento == usuario.numero_documento
                for existente in self._usuarios.values()
            ):
                raise DocumentoDuplicadoError()

            usuario_guardado = replace(usuario, id=self._siguiente_id)
            self._usuarios[usuario_guardado.id] = usuario_guardado
            self._siguiente_id += 1
            return usuario_guardado

    def buscar_por_correo(self, correo: str) -> Usuario | None:
        correo_normalizado = correo.strip().casefold()
        with self._lock:
            return next(
                (
                    usuario
                    for usuario in self._usuarios.values()
                    if usuario.correo.casefold() == correo_normalizado
                ),
                None,
            )

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        with self._lock:
            return self._usuarios.get(usuario_id)

    def activar(
        self, usuario_id: int, fecha_activacion: datetime
    ) -> Usuario | None:
        with self._lock:
            usuario = self._usuarios.get(usuario_id)
            if usuario is None:
                return None
            usuario_actualizado = replace(
                usuario,
                estado="ACTIVA",
                fecha_activacion=fecha_activacion,
            )
            self._usuarios[usuario_id] = usuario_actualizado
            return usuario_actualizado
