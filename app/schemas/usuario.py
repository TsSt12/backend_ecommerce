from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UsuarioCreate(BaseModel):
    """Registro de un nuevo usuario. El consentimiento debe ser explícito."""
    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)
    acepto_tratamiento: bool

    @field_validator("acepto_tratamiento")
    @classmethod
    def debe_aceptar(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "Debe aceptar el tratamiento de datos personales (Ley 25.326)"
            )
        return v


class UsuarioOut(BaseModel):
    """Respuesta de usuario — nunca incluye el hash de contraseña."""
    id: int
    nombre: str
    email: EmailStr
    rol: str
    acepto_tratamiento: bool
    fecha_consentimiento: datetime | None = None
    activo: bool
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
