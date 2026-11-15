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
from app.domain.models.parametros_alojamiento_alimentacion import (
    CategoriaAlojamientoAlimentacionCreate,
    RESTRICCION_ALIMENTARIA,
    TIPO_ALIMENTACION,
    TIPO_HABITACION,
    ValorAlojamientoAlimentacionCreate,
)


_PARAMETROS_INICIALES = (
    (
        CategoriaAlojamientoAlimentacionCreate(
            clave=TIPO_HABITACION,
            nombre="Tipo de habitación",
            descripcion="Tipos de habitación disponibles",
        ),
        (
            ValorAlojamientoAlimentacionCreate(
                codigo="SENCILLA",
                nombre="Sencilla",
                descripcion="Habitación sencilla",
                orden=1,
            ),
            ValorAlojamientoAlimentacionCreate(
                codigo="FAMILIAR",
                nombre="Familiar",
                descripcion="Habitación familiar",
                orden=2,
            ),
        ),
    ),
    (
        CategoriaAlojamientoAlimentacionCreate(
            clave=TIPO_ALIMENTACION,
            nombre="Tipo de alimentación",
            descripcion="Tipos de alimentación disponibles",
        ),
        (
            ValorAlojamientoAlimentacionCreate(
                codigo="DESAYUNO",
                nombre="Solo desayuno",
                descripcion="Incluye solo desayuno",
                orden=1,
            ),
        ),
    ),
    (
        CategoriaAlojamientoAlimentacionCreate(
            clave=RESTRICCION_ALIMENTARIA,
            nombre="Restricción alimentaria",
            descripcion="Restricciones alimentarias disponibles",
        ),
        (
            ValorAlojamientoAlimentacionCreate(
                codigo="VEGETARIANA",
                nombre="Vegetariana",
                descripcion="Alimentación vegetariana",
                orden=1,
            ),
        ),
    ),
)


class CargarParametrosAlojamientoAlimentacion:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> None:
        for datos_categoria, valores_iniciales in _PARAMETROS_INICIALES:
            categoria = next(
                (
                    item
                    for item in self._categorias.listar()
                    if item.clave.casefold() == datos_categoria.clave.casefold()
                ),
                None,
            )
            if categoria is None:
                try:
                    categoria = self._categorias.crear(
                        CategoriaParametro(
                            id=0,
                            clave=datos_categoria.clave,
                            nombre=datos_categoria.nombre,
                            descripcion=datos_categoria.descripcion,
                        )
                    )
                except CategoriaParametroDuplicadaError:
                    categoria = next(
                        (
                            item
                            for item in self._categorias.listar()
                            if item.clave.casefold()
                            == datos_categoria.clave.casefold()
                        ),
                        None,
                    )
            if categoria is None:
                continue

            codigos_existentes = {
                valor.codigo.casefold()
                for valor in self._valores.listar(categoria.clave)
            }
            for valor_inicial in valores_iniciales:
                if valor_inicial.codigo.casefold() in codigos_existentes:
                    continue
                try:
                    self._valores.crear(
                        categoria=categoria.clave,
                        codigo=valor_inicial.codigo,
                        nombre=valor_inicial.nombre,
                        descripcion=valor_inicial.descripcion,
                        orden=valor_inicial.orden,
                        es_sistema=False,
                    )
                except ValorCategoriaDuplicadoError:
                    continue
                codigos_existentes.add(valor_inicial.codigo.casefold())
