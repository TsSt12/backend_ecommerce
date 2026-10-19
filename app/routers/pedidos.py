from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.pedido import PedidoCreate, PedidoOut
from app.schemas.revocacion import RevocacionOut
from app.services import pedido_service, revocacion_service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post("/", response_model=PedidoOut, status_code=201)
def crear(
    datos: PedidoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return pedido_service.crear_pedido(db, current_user, datos)


# IMPORTANTE: esta ruta DEBE declararse ANTES que /{pedido_id}
# Si estuviera después, FastAPI intentaría convertir "mios" en int → 422
@router.get("/mios", response_model=list[PedidoOut])
def mis_pedidos(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return pedido_service.listar_mis_pedidos(db, current_user)


@router.get("/{pedido_id}", response_model=PedidoOut)
def detalle(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return pedido_service.obtener_pedido(db, pedido_id, current_user)


@router.post("/{pedido_id}/revocacion", response_model=RevocacionOut, status_code=201)
def revocar(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return revocacion_service.revocar(db, current_user, pedido_id)
