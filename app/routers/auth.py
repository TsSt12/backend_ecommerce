from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.usuario import RefreshRequest, Token, UsuarioCreate, UsuarioOut
from app.services import usuario_service as service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UsuarioOut, status_code=201)
def registrar(datos: UsuarioCreate, db: Session = Depends(get_db)):
    return service.registrar_usuario(db, datos)


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """El campo `username` lleva el email del usuario."""
    usuario = service.autenticar_usuario(db, email=form.username, password=form.password)
    return service.generar_tokens(usuario)


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    return service.refrescar_tokens(db, body.refresh_token)


@router.get("/me", response_model=UsuarioOut)
def me(current_user=Depends(get_current_user)):
    return current_user
