from dataclasses import replace
from datetime import datetime
from threading import Lock

from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.sesion import SesionInvalidaOCerradaError
from app.domain.interfaces.sesion import SesionRepository
from app.domain.models.sesion import SesionCreate


class InMemorySesionRepository(SesionRepository):
    def __init__(self) -> None:
        self._sesiones: dict[int, SesionUsuario] = {}
        self._ids_por_token_hash: dict[str, int] = {}
        self._siguiente_id = 1
        self._lock = Lock()

    def crear(self, sesion: SesionCreate) -> SesionUsuario:
        with self._lock:
            if sesion.token_hash in self._ids_por_token_hash:
                raise ValueError("El hash del token ya está registrado")
            creada = SesionUsuario(
                id=self._siguiente_id,
                usuario_id=sesion.usuario_id,
                correo=sesion.correo,
                rol=sesion.rol,
                token_hash=sesion.token_hash,
                inicio_en=sesion.inicio_en,
                ultima_actividad=sesion.inicio_en,
                expira_en=sesion.expira_en,
                activa=True,
                motivo_cierre=None,
                cerrada_en=None,
            )
            self._sesiones[creada.id] = creada
            self._ids_por_token_hash[creada.token_hash] = creada.id
            self._siguiente_id += 1
            return creada

    def buscar_por_token_hash(self, token_hash: str) -> SesionUsuario | None:
        with self._lock:
            sesion_id = self._ids_por_token_hash.get(token_hash)
            return self._sesiones.get(sesion_id) if sesion_id is not None else None

    def actualizar_actividad(
        self, token_hash: str, ultima_actividad: datetime
    ) -> SesionUsuario:
        with self._lock:
            sesion = self._obtener_activa(token_hash)
            actualizada = sesion.actualizar_actividad(ultima_actividad)
            self._sesiones[sesion.id] = actualizada
            return actualizada

    def renovar_token(
        self,
        token_hash_actual: str,
        token_hash_nuevo: str,
        ultima_actividad: datetime,
        expira_en: datetime,
    ) -> SesionUsuario:
        with self._lock:
            sesion = self._obtener_activa(token_hash_actual)
            if token_hash_nuevo in self._ids_por_token_hash:
                raise ValueError("El hash del nuevo token ya está registrado")
            renovada = sesion.renovar(
                token_hash_nuevo, ultima_actividad, expira_en
            )
            del self._ids_por_token_hash[token_hash_actual]
            self._ids_por_token_hash[token_hash_nuevo] = sesion.id
            self._sesiones[sesion.id] = renovada
            return renovada

    def cerrar_por_inactividad(
        self, token_hash: str, cerrada_en: datetime
    ) -> SesionUsuario:
        return self._cerrar(token_hash, "INACTIVIDAD", cerrada_en)

    def cerrar_por_logout(
        self, token_hash: str, cerrada_en: datetime
    ) -> SesionUsuario:
        return self._cerrar(token_hash, "LOGOUT", cerrada_en)

    def _cerrar(
        self,
        token_hash: str,
        motivo: str,
        cerrada_en: datetime,
    ) -> SesionUsuario:
        with self._lock:
            sesion = self._obtener_activa(token_hash)
            cerrada = sesion.cerrar(motivo, cerrada_en)
            self._sesiones[sesion.id] = cerrada
            return cerrada

    def _obtener_activa(self, token_hash: str) -> SesionUsuario:
        sesion_id = self._ids_por_token_hash.get(token_hash)
        sesion = self._sesiones.get(sesion_id) if sesion_id is not None else None
        if sesion is None or not sesion.activa:
            raise SesionInvalidaOCerradaError()
        return sesion