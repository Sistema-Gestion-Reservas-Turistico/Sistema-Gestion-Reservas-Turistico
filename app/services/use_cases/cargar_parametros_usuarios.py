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
from app.domain.models.usuarios import TIPO_DOCUMENTO


_TIPOS_DOCUMENTO = (
    ("CC", "Cédula de ciudadanía"),
    ("CE", "Cédula de extranjería"),
    ("PASAPORTE", "Pasaporte"),
)


class CargarParametrosUsuarios:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores

    def ejecutar(self) -> None:
        categoria = next(
            (
                item
                for item in self._categorias.listar()
                if item.clave.casefold() == TIPO_DOCUMENTO.casefold()
            ),
            None,
        )
        if categoria is None:
            try:
                categoria = self._categorias.crear(
                    CategoriaParametro(
                        id=0,
                        clave=TIPO_DOCUMENTO,
                        nombre="Tipo de documento",
                        descripcion="Tipos de documento de identidad aceptados",
                    )
                )
            except CategoriaParametroDuplicadaError:
                categoria = next(
                    (
                        item
                        for item in self._categorias.listar()
                        if item.clave.casefold() == TIPO_DOCUMENTO.casefold()
                    ),
                    None,
                )
        if categoria is None:
            return

        existentes = {
            valor.codigo.casefold(): valor
            for valor in self._valores.listar(categoria.clave)
        }
        for orden, (codigo, nombre) in enumerate(_TIPOS_DOCUMENTO, 1):
            existente = existentes.get(codigo.casefold())
            if existente is not None:
                if not existente.activo:
                    self._valores.actualizar_estado(
                        categoria.clave, existente.id, activo=True
                    )
                continue
            try:
                self._valores.crear(
                    categoria=categoria.clave,
                    codigo=codigo,
                    nombre=nombre,
                    descripcion=nombre,
                    orden=orden,
                    es_sistema=True,
                )
            except ValorCategoriaDuplicadoError:
                continue
