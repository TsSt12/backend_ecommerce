from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verificar_password, crear_token, decodificar_token
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate
from jose import JWTError


def registrar_usuario(db: Session, datos: UsuarioCreate) -> Usuario:
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    usuario = Usuario(
        nombre=datos.nombre,
        email=datos.email,
        hashed_password=hash_password(datos.password),
        acepto_tratamiento=True,
        fecha_consentimiento=datetime.now(timezone.utc),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar_usuario(db: Session, email: str, password: str) -> Usuario:
    """Retorna el usuario si las credenciales son válidas. Nunca revela cuál campo falló."""
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales incorrectas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not usuario or not verificar_password(password, usuario.hashed_password):
        raise error
    # [Clase 9] — descomentá cuando exista la columna `activo`
    if not usuario.activo:
        raise error
    return usuario


def generar_tokens(usuario: Usuario) -> dict:
    payload = {"sub": str(usuario.id), "rol": usuario.rol}
    return {
        "access_token": crear_token(payload, tipo="access"),
        "refresh_token": crear_token(payload, tipo="refresh"),
        "token_type": "bearer",
    }


def refrescar_tokens(db: Session, refresh_token: str) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de refresco inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(refresh_token)
        if payload.get("tipo") != "refresh":
            raise exc
        sub = payload.get("sub")
        if sub is None:
            raise exc
    except JWTError:
        raise exc

    usuario = db.query(Usuario).filter(Usuario.id == int(sub)).first()
    if not usuario or not usuario.activo:
        raise exc
    return generar_tokens(usuario)
