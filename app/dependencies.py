from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.db.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# Dependencia de base de datos
# ---------------------------------------------------------------------------
def get_db():
    """Provee una sesión de DB y la cierra al terminar el request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Dependencia de usuario autenticado
# ---------------------------------------------------------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Valida el JWT y devuelve el usuario activo."""
    from app.models.usuario import Usuario  # import local para evitar circulares

    credenciales_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        if payload.get("tipo") != "access":
            raise credenciales_exc
        sub: str = payload.get("sub")
        if sub is None:
            raise credenciales_exc
    except JWTError:
        raise credenciales_exc

    usuario = db.query(Usuario).filter(Usuario.id == int(sub)).first()
    if usuario is None:
        raise credenciales_exc

    # [Clase 9] descomentá cuando el campo `activo` exista en la base
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta dada de baja",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario


# ---------------------------------------------------------------------------
# Dependencia de administrador
# ---------------------------------------------------------------------------
def require_admin(current_user=Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return current_user
