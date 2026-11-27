from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.exceptions.categorias_parametros import (
    CategoriaParametroDuplicadaError,
)
from app.domain.exceptions.valores_categorias_domain import (
    ValorCategoriaDuplicadoError,
)
from app.domain.interfaces.categorias_parametros_domain import (
    CategoriaParametroRepository,
)
from app.domain.interfaces.valores_categorias_domain import ValoresCategoriaRepository
from app.services.use_cases.listar_parametros_transporte import (
    ESTADO_VEHICULO,
    TIPO_VEHICULO,
)


_PARAMETROS_INICIALES = (
    (
        TIPO_VEHICULO,
        "Tipo de vehiculo",
        "Tipos de vehiculo disponibles para transporte",
        (
            ("AUTOMOVIL", "Automovil"),
            ("CAMIONETA", "Camioneta"),
            ("MINIBUS", "Minibus"),
            ("AUTOBUS", "Autobus"),
        ),
    ),
    (
        ESTADO_VEHICULO,
        "Estado del vehiculo",
        "Estados operativos de los vehiculos",
        (
            ("DISPONIBLE", "Disponible"),
            ("EN_MANTENIMIENTO", "En mantenimiento"),
            ("FUERA_DE_SERVICIO", "Fuera de servicio"),
        ),
    ),
)


class CargarParametrosTransporte:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> None:
        for clave, nombre, descripcion, valores_iniciales in _PARAMETROS_INICIALES:
            categoria = next(
                (
                    item
                    for item in self._categorias.listar()
                    if item.clave.casefold() == clave.casefold()
                ),
                None,
            )
            if categoria is None:
                try:
                    categoria = self._categorias.crear(
                        CategoriaParametro(
                            id=0,
                            clave=clave,
                            nombre=nombre,
                            descripcion=descripcion,
                        )
                    )
                except CategoriaParametroDuplicadaError:
                    categoria = next(
                        (
                            item
                            for item in self._categorias.listar()
                            if item.clave.casefold() == clave.casefold()
                        ),
                        None,
                    )
            if categoria is None:
                continue

            codigos_existentes = {
                valor.codigo.casefold()
                for valor in self._valores.listar(categoria.clave)
            }
            for orden, (codigo, nombre_valor) in enumerate(valores_iniciales, 1):
                if codigo.casefold() in codigos_existentes:
                    continue
                try:
                    self._valores.crear(
                        categoria=categoria.clave,
                        codigo=codigo,
                        nombre=nombre_valor,
                        descripcion=nombre_valor,
                        orden=orden,
                        es_sistema=True,
                    )
                except ValorCategoriaDuplicadoError:
                    continue
                codigos_existentes.add(codigo.casefold())