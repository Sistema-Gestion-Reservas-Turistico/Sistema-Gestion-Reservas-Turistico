from app.domain.models.autocompletar_ubicaciones import (
    AutocompletarUbicacionesData,
    AutocompletarUbicacionesResponse,
    ErrorAutocompletarResponse,
    SugerenciaUbicacionItem,
)
from app.domain.exceptions.autocompletar_ubicaciones import (
    ConsultaAutocompletarInvalidaError,
    PersistenciaAutocompletarError,
)


def test_modelos_de_respuesta_conservan_departamento_nulo() -> None:
    sugerencia = SugerenciaUbicacionItem(63, "Quindío", "DEPARTAMENTO")
    respuesta = AutocompletarUbicacionesResponse(
        "Sugerencias de ubicación encontradas",
        AutocompletarUbicacionesData("qui", 1, [sugerencia]),
        True,
    )
    assert respuesta.data.sugerencias[0].departamento is None
    assert ErrorAutocompletarResponse("error").data is None


def test_excepciones_tienen_mensajes_de_dominio() -> None:
    assert str(ConsultaAutocompletarInvalidaError()) == (
        "El texto de búsqueda debe tener al menos 3 caracteres"
    )
    assert str(PersistenciaAutocompletarError()) == (
        "No fue posible consultar las sugerencias de ubicación"
    )