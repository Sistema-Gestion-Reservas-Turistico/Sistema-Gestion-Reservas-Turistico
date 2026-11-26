from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from app.api.responses import ApiErrorResponse, ApiResponse

from app.domain.models.autenticacion import LoginRequest


class LoginRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: str = Field(
        strict=True,
        min_length=1,
        validation_alias=AliasChoices("email", "correo"),
    )
    password: str = Field(strict=True, min_length=1, repr=False)

    def to_domain(self) -> LoginRequest:
        return LoginRequest(correo=self.email, password=self.password)


class UsuarioAutenticadoData(BaseModel):
    id: int
    first_name: str
    last_name: str
    role: str


class LoginExitosoData(BaseModel):
    token: str
    token_type: str
    expires_in: int
    inactivity_timeout: int
    user: UsuarioAutenticadoData


class LoginExitosoResponse(ApiResponse[LoginExitosoData]):
    pass


class LoginErrorCredencialesData(BaseModel):
    attempts_remaining: int


class LoginBloqueadoData(BaseModel):
    locked_until: str
    minutes_remaining: int


class LoginErrorResponse(ApiErrorResponse):
    pass


class LoginErrorCredencialesResponse(LoginErrorResponse):
    data: LoginErrorCredencialesData


class LoginBloqueadoResponse(LoginErrorResponse):
    data: LoginBloqueadoData
