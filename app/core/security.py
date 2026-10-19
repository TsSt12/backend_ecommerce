from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def crear_token(data: dict, tipo: str = "access") -> str:
    """Crea un JWT firmado. `tipo` puede ser 'access' o 'refresh'."""
    minutos = settings.ACCESS_MIN if tipo == "access" else settings.REFRESH_MIN
    payload = data.copy()
    payload.update({
        "tipo": tipo,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutos),
    })
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decodifica y valida la firma del token. Lanza JWTError si es inválido."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
