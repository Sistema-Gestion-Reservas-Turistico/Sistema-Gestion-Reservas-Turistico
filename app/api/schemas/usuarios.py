import re

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from app.domain.models.usuarios import UsuarioRegistroCreate


class UsuarioRegistroRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tipo_documento: str = Field(strict=True, min_length=1)
    numero_documento: str = Field(strict=True, min_length=1, max_length=20)
    nombres: str = Field(strict=True, min_length=1)
    apellidos: str = Field(strict=True, min_length=1)
    correo: str = Field(strict=True, min_length=3)
    password: str = Field(strict=True, min_length=8, repr=False)
    acepta_tratamiento_datos: StrictBool
    telefono: str | None = Field(default=None, strict=True)

    @field_validator("tipo_documento", "nombres", "apellidos")
    @classmethod
    def validar_texto_obligatorio(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Este campo es obligatorio")
        return valor

    @field_validator("numero_documento")
    @classmethod
    def validar_numero_documento(cls, valor: str) -> str:
        if not valor.isalnum():
            raise ValueError("Debe contener solo caracteres alfanuméricos")
        return valor

    @field_validator("correo")
    @classmethod
    def normalizar_y_validar_correo(cls, valor: str) -> str:
        correo = valor.strip().casefold()
        local, separator, domain = correo.partition("@")
        patron = re.compile(
            r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
            r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
            r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
        )
        if (
            not separator
            or not local
            or not domain
            or local.startswith(".")
            or ".." in local
            or not patron.fullmatch(correo)
        ):
            raise ValueError("Debe ser un correo válido")
        return correo

    @field_validator("password")
    @classmethod
    def validar_password(cls, valor: str) -> str:
        if (
            not re.search(r"[A-Z]", valor)
            or not re.search(r"[a-z]", valor)
            or not re.search(r"\d", valor)
        ):
            raise ValueError(
                "Debe tener mínimo 8 caracteres, una mayúscula, "
                "una minúscula y un número"
            )
        return valor

    @field_validator("telefono")
    @classmethod
    def normalizar_telefono(cls, valor: str | None) -> str | None:
        if valor is None:
            return None
        telefono = valor.strip()
        return telefono or None

    def to_domain(self) -> UsuarioRegistroCreate:
        return UsuarioRegistroCreate(
            tipo_documento=self.tipo_documento,
            numero_documento=self.numero_documento,
            nombres=self.nombres,
            apellidos=self.apellidos,
            correo=self.correo,
            password=self.password,
            acepta_tratamiento_datos=self.acepta_tratamiento_datos,
            telefono=self.telefono,
        )


class UsuarioRegistroData(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: str
    estado: str


class UsuarioRegistroResponse(BaseModel):
    mensaje: str
    data: UsuarioRegistroData
    success: bool


class ErrorCampoRegistro(BaseModel):
    campo: str
    detalle: str


class ErrorRegistroData(BaseModel):
    errores: list[ErrorCampoRegistro]


class ErrorRegistroResponse(BaseModel):
    mensaje: str
    data: ErrorRegistroData | None = None
    success: bool = False
