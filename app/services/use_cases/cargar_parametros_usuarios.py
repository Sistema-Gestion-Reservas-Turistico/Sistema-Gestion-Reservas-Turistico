from datetime import datetime, timedelta, timezone

from app.domain.entities.categoria_parametro import CategoriaParametro
from app.domain.entities.usuario import Usuario
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
from app.domain.interfaces.usuarios import UsuarioRepository
from app.domain.models.usuarios import TIPO_DOCUMENTO
from app.services.security.passwords import hash_password


_TIPOS_DOCUMENTO = (
    ("CC", "Cédula de ciudadanía"),
    ("CE", "Cédula de extranjería"),
    ("PASAPORTE", "Pasaporte"),
)
_ZONA_HORARIA = timezone(timedelta(hours=-5), name="COT")


class CargarParametrosUsuarios:
    def __init__(
        self,
        categorias: CategoriaParametroRepository,
        valores: ValoresCategoriaRepository,
        usuarios: UsuarioRepository,
    ) -> None:
        self._categorias = categorias
        self._valores = valores
        self._usuarios = usuarios

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
        self._crear_usuario_prueba()

    def _crear_usuario_prueba(self) -> None:
        correo = "cliente.activo@correo.com"
        if self._usuarios.buscar_por_correo(correo) is not None:
            return
        ahora = datetime.now(_ZONA_HORARIA)
        self._usuarios.registrar(
            Usuario(
                id=0,
                tipo_documento="CC",
                numero_documento="PRUEBA001",
                nombres="Cliente",
                apellidos="Prueba",
                correo=correo,
                telefono=None,
                password_hash=hash_password("Viaje2026"),
                rol="Cliente",
                estado="ACTIVO",
                acepta_tratamiento_datos=True,
                fecha_aceptacion_datos=ahora,
                intentos_fallidos=0,
                bloqueado_hasta=None,
                creado_en=ahora,
            )
        )
