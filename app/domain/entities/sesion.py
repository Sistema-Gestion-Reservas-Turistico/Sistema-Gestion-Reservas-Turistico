from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Literal

from app.config import MINUTOS_INACTIVIDAD_SESION
from app.domain.exceptions.sesion import (
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)


MotivoCierreSesion = Literal["INACTIVIDAD", "LOGOUT"]


@dataclass(frozen=True)
class SesionUsuario:
    id: int
    usuario_id: int
    correo: str
    rol: str
    token_hash: str
    inicio_en: datetime
    ultima_actividad: datetime
    expira_en: datetime
    activa: bool
    motivo_cierre: MotivoCierreSesion | None
    cerrada_en: datetime | None

    def supero_limite_inactividad(
        self,
        ahora: datetime,
        tiempo_max_inactividad: timedelta | None = None,
    ) -> bool:
        limite = tiempo_max_inactividad or timedelta(
            minutes=MINUTOS_INACTIVIDAD_SESION
        )
        return ahora - self.ultima_actividad > limite

    def validar_vigencia(self, ahora: datetime) -> None:
        if ahora >= self.expira_en:
            raise SesionInvalidaOCerradaError()

    def validar_para_uso(
        self,
        ahora: datetime,
        tiempo_max_inactividad: timedelta | None = None,
    ) -> None:
        if not self.activa:
            if self.motivo_cierre == "INACTIVIDAD":
                raise SesionCerradaPorInactividadError()
            raise SesionInvalidaOCerradaError()
        self.validar_vigencia(ahora)
        if self.supero_limite_inactividad(ahora, tiempo_max_inactividad):
            raise SesionCerradaPorInactividadError()

    def actualizar_actividad(self, ahora: datetime) -> "SesionUsuario":
        if not self.activa:
            raise SesionInvalidaOCerradaError()
        return replace(self, ultima_actividad=ahora)

    def renovar(
        self,
        token_hash: str,
        ahora: datetime,
        expira_en: datetime,
    ) -> "SesionUsuario":
        if not self.activa:
            raise SesionInvalidaOCerradaError()
        return replace(
            self,
            token_hash=token_hash,
            ultima_actividad=ahora,
            expira_en=expira_en,
        )

    def cerrar(
        self,
        motivo: MotivoCierreSesion,
        cerrada_en: datetime,
    ) -> "SesionUsuario":
        if not self.activa:
            raise SesionInvalidaOCerradaError()
        return replace(
            self,
            activa=False,
            motivo_cierre=motivo,
            cerrada_en=cerrada_en,
        )