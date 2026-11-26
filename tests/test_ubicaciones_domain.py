from app.domain.entities.departamento import Departamento
from app.domain.entities.municipio import Municipio, MunicipioTerritorial
from app.domain.entities.pais import Pais
from app.domain.models.ubicaciones import (
    ConsultaUbicacionesData,
    ConsultaUbicacionesResponse,
    ErrorUbicacionesResponse,
    UbicacionItem,
)


def test_entidades_territoriales_mantienen_jerarquia() -> None:
    assert Pais(1, "Colombia").nombre == "Colombia"
    assert Departamento(63, 1, "Quindío").id_pais == 1
    municipio = Municipio(
        63690,
        4.55,
        4.72,
        -75.66,
        -75.46,
        "Salento",
        63,
    )
    assert municipio.habilitado is True
    assert municipio.id_departamento == 63


def test_constructor_territorial_hu12_sigue_compatible() -> None:
    municipio = MunicipioTerritorial(63690, 4.55, 4.72, -75.66, -75.46)
    assert municipio.habilitado is True
    assert municipio.nombre == ""


def test_modelos_de_respuesta_de_ubicaciones() -> None:
    ubicacion = UbicacionItem(63, "Quindío")
    datos = ConsultaUbicacionesData("DEPARTAMENTO", 1, 1, [ubicacion])
    respuesta = ConsultaUbicacionesResponse(
        "Consulta de ubicaciones exitosa", datos, True
    )
    error = ErrorUbicacionesResponse("Fallo")
    assert respuesta.data.ubicaciones == [ubicacion]
    assert error.data is None
    assert error.success is False