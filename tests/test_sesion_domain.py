from datetime import datetime, timedelta, timezone

import pytest

from app.domain.entities.sesion import SesionUsuario
from app.domain.exceptions.sesion import (
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)
from app.domain.models.sesion import (
    CerrarSesionRequest,
    CerrarSesionResponse,
    MantenerSesionRequest,
    SesionActualResponse,
    SesionCreate,
    SesionRenovadaResponse,
)
from app.api.schemas.sesion import (
    SesionActualApiResponse,
    SesionActualData,
    SesionRenovadaApiResponse,
    SesionRenovadaData,
)


@pytest.fixture
def sesion() -> SesionUsuario:
    inicio = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    return SesionUsuario(
        id=1,
        usuario_id=7,
        correo="cliente@correo.com",
        rol="Cliente",
        token_hash="hash",
        inicio_en=inicio,
        ultima_actividad=inicio,
        expira_en=inicio + timedelta(minutes=30),
        activa=True,
        motivo_cierre=None,
        cerrada_en=None,
    )


def test_limite_de_inactividad_es_exclusivo(sesion: SesionUsuario) -> None:
    ahora = sesion.ultima_actividad + timedelta(minutes=15)
    sesion.validar_para_uso(ahora, timedelta(minutes=15))


def test_superar_limite_de_inactividad_cierra_logicamente(
    sesion: SesionUsuario,
) -> None:
    ahora = sesion.ultima_actividad + timedelta(minutes=15, microseconds=1)
    with pytest.raises(SesionCerradaPorInactividadError):
        sesion.validar_para_uso(ahora, timedelta(minutes=15))


def test_token_expira_en_el_instante_limite(sesion: SesionUsuario) -> None:
    with pytest.raises(SesionInvalidaOCerradaError):
        sesion.validar_para_uso(sesion.expira_en, timedelta(minutes=15))


def test_sesion_cerrada_por_logout_no_se_puede_usar(
    sesion: SesionUsuario,
) -> None:
    cerrada = sesion.cerrar("LOGOUT", sesion.inicio_en)
    with pytest.raises(SesionInvalidaOCerradaError):
        cerrada.validar_para_uso(sesion.inicio_en, timedelta(minutes=15))


def test_sesion_cerrada_por_inactividad_conserva_error_especifico(
    sesion: SesionUsuario,
) -> None:
    cerrada = sesion.cerrar("INACTIVIDAD", sesion.inicio_en)
    with pytest.raises(SesionCerradaPorInactividadError):
        cerrada.validar_para_uso(sesion.inicio_en, timedelta(minutes=15))


def test_modelos_de_sesion_ocultan_tokens_y_conservan_datos() -> None:
    ahora = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    creacion = SesionCreate(
        usuario_id=7,
        correo="cliente@correo.com",
        rol="Cliente",
        token_hash="hash-secreto",
        inicio_en=ahora,
        expira_en=ahora + timedelta(minutes=30),
    )
    mantener = MantenerSesionRequest(token="token-plano")
    cerrar = CerrarSesionRequest(token="token-plano")
    renovada = SesionRenovadaResponse("token-nuevo", "Bearer", 1800, 900)
    actual = SesionActualResponse(7, "cliente@correo.com", "Cliente", ahora, ahora, 900)
    cerrada = CerrarSesionResponse("Cerrada", "LOGOUT", ahora)

    assert "hash-secreto" not in repr(creacion)
    assert "token-plano" not in repr(mantener)
    assert "token-plano" not in repr(cerrar)
    assert renovada.expira_en == 1800
    assert actual.ultima_actividad == ahora
    assert cerrada.motivo_cierre == "LOGOUT"


def test_esquemas_pydantic_de_sesion_validan_respuestas() -> None:
    ahora = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    renovada = SesionRenovadaApiResponse(
        success=True,
        message="Sesión renovada",
        data=SesionRenovadaData(
            token="token-nuevo",
            token_type="Bearer",
            expires_in=1800,
            inactivity_timeout=900,
        ),
    )
    actual = SesionActualApiResponse(
        success=True,
        message="Current session retrieved successfully",
        data=SesionActualData(
            user_id=7,
            email="cliente@correo.com",
            role="Cliente",
            started_at=ahora,
            last_activity=ahora,
            inactivity_timeout=900,
        ),
    )
    assert renovada.data.token_type == "Bearer"
    assert actual.data.user_id == 7