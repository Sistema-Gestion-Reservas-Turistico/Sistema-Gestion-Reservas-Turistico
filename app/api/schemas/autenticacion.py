from pydantic import BaseModel, ConfigDict, Field

from app.domain.models.autenticacion import LoginRequest


class LoginRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    correo: str = Field(strict=True, min_length=1)
    password: str = Field(strict=True, min_length=1, repr=False)

    def to_domain(self) -> LoginRequest:
        return LoginRequest(correo=self.correo, password=self.password)


class LoginExitosoData(BaseModel):
    id: int
    nombres: str
    apellidos: str
    correo: str
    rol: str


class LoginExitosoResponse(BaseModel):
    mensaje: str
    data: LoginExitosoData
    success: bool


class LoginErrorCredencialesData(BaseModel):
    intentos_restantes: int


class LoginBloqueadoData(BaseModel):
    bloqueada_hasta: str
    minutos_restantes: int


class LoginErrorResponse(BaseModel):
    mensaje: str
    data: LoginErrorCredencialesData | LoginBloqueadoData | None = None
    success: bool = False


class LoginErrorCredencialesResponse(LoginErrorResponse):
    data: LoginErrorCredencialesData


class LoginBloqueadoResponse(LoginErrorResponse):
    data: LoginBloqueadoData
