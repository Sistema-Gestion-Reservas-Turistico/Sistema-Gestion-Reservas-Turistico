from datetime import datetime, timedelta, timezone

from app.domain.entities.municipio import MunicipioTerritorial
from app.repositories.adapters.in_memory_territorio_repository import (
    InMemoryTerritorioRepository,
)


def test_fecha_por_defecto_usa_offset_menos_cinco() -> None:
    municipio = MunicipioTerritorial(1, 0, 1, 0, 1)
    assert municipio.fecha_actualizacion.utcoffset() == -timedelta(hours=5)


def test_repositorio_actualiza_municipio_sin_perder_otros_campos() -> None:
    repositorio = InMemoryTerritorioRepository()
    fecha_original = datetime(2026, 10, 25, 15, 0, tzinfo=timezone.utc)
    municipio = MunicipioTerritorial(
        63130,
        4.48,
        4.57,
        -75.72,
        -75.60,
        "Calarcá",
        63,
        False,
        fecha_original,
    )
    repositorio.crear_municipio_si_no_existe(municipio)
    fecha_nueva = datetime(2026, 10, 25, 15, 10, tzinfo=timezone.utc)

    actualizado = repositorio.actualizar_disponibilidad_municipio(
        63130, True, fecha_nueva
    )

    assert actualizado is not None
    assert actualizado.habilitado is True
    assert actualizado.fecha_actualizacion == fecha_nueva
    assert actualizado.nombre == "Calarcá"
    assert actualizado.id_departamento == 63
    assert repositorio.obtener_municipio(63130) == actualizado