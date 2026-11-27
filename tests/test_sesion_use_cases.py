import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from app.domain.exceptions.sesion import (
    SesionCerradaPorInactividadError,
    SesionInvalidaOCerradaError,
)
from app.repositories.adapters.in_memory_sesion_repository import (
    InMemorySesionRepository,
)
from app.services.use_cases.cerrar_sesion import CerrarSesionUseCase
from app.services.use_cases.crear_sesion_usuario import CrearSesionUsuarioUseCase
from app.services.use_cases.mantener_sesion import MantenerSesionUseCase
from app.services.use_cases.validar_actividad_sesion import (
    ValidarActividadSesionUseCase,
)


@pytest.fixture
def contexto() -> tuple[InMemorySesionRepository, datetime, str]:
    repositorio = InMemorySesionRepository()
    ahora = datetime.now(timezone.utc)
    sesion = CrearSesionUsuarioUseCase(repositorio).ejecutar(
        7, "cliente@correo.com", "Cliente", ahora
    )
    return repositorio, ahora, sesion.token


def test_crear_guarda_solo_el_hash_del_token(
    contexto: tuple[InMemorySesionRepository, datetime, str],
) -> None:
    repositorio, _, token = contexto
    sesion = repositorio.buscar_por_token_hash(
        hashlib.sha256(token.encode("utf-8")).hexdigest()
    )
    assert sesion is not None
    assert sesion.token_hash != token
    assert token not in repr(sesion)


def test_validar_actividad_actualiza_ultima_actividad(
    contexto: tuple[InMemorySesionRepository, datetime, str],
) -> None:
    repositorio, ahora, token = contexto
    actividad = ahora + timedelta(minutes=2)
    sesion = ValidarActividadSesionUseCase(repositorio).ejecutar(token, actividad)
    assert sesion.ultima_actividad == actividad


def test_inactividad_cierra_la_sesion(
    contexto: tuple[InMemorySesionRepository, datetime, str],
) -> None:
    repositorio, ahora, token = contexto
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with pytest.raises(SesionCerradaPorInactividadError):
        ValidarActividadSesionUseCase(repositorio).ejecutar(
            token, ahora + timedelta(minutes=15, microseconds=1)
        )
    sesion = repositorio.buscar_por_token_hash(token_hash)
    assert sesion is not None
    assert sesion.activa is False
    assert sesion.motivo_cierre == "INACTIVIDAD"


def test_mantener_rota_el_token_e_invalida_el_anterior(
    contexto: tuple[InMemorySesionRepository, datetime, str],
) -> None:
    repositorio, ahora, token = contexto
    renovada = MantenerSesionUseCase(repositorio).ejecutar(
        token, ahora + timedelta(minutes=1)
    )
    assert renovada.token != token
    assert repositorio.buscar_por_token_hash(
        hashlib.sha256(token.encode("utf-8")).hexdigest()
    ) is None
    assert repositorio.buscar_por_token_hash(
        hashlib.sha256(renovada.token.encode("utf-8")).hexdigest()
    ) is not None
    with pytest.raises(SesionInvalidaOCerradaError):
        MantenerSesionUseCase(repositorio).ejecutar(token, ahora)


def test_logout_invalida_el_token(
    contexto: tuple[InMemorySesionRepository, datetime, str],
) -> None:
    repositorio, ahora, token = contexto
    respuesta = CerrarSesionUseCase(repositorio).ejecutar(token, ahora)
    assert respuesta.motivo_cierre == "LOGOUT"
    with pytest.raises(SesionInvalidaOCerradaError):
        ValidarActividadSesionUseCase(repositorio).ejecutar(token, ahora)