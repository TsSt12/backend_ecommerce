import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.revocacion import SolicitudRevocacion
from app.models.usuario import Usuario

PLAZO_DIAS = 10   # art. 34 Ley 24.240


def generar_codigo() -> str:
    """Genera un código único de revocación. Ej.: ARR-20260914-A3F9C1"""
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    sufijo = secrets.token_hex(3).upper()
    return f"ARR-{fecha}-{sufijo}"


def revocar(db: Session, usuario: Usuario, pedido_id: int) -> SolicitudRevocacion:
    """
    Validaciones en orden (más baratas primero):
    1. El pedido existe y es del usuario (404 si no).
    2. No está ya cancelado (409).
    3. Está dentro del plazo de 10 días corridos (409).
    4. Transacción: devolver stock, marcar cancelado, crear solicitud.
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido or pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pedido no encontrado")

    if pedido.estado == "cancelado":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="El pedido ya fue cancelado")

    ahora = datetime.now(timezone.utc)
    limite = pedido.creado_en + timedelta(days=PLAZO_DIAS)
    if ahora > limite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Fuera del plazo de arrepentimiento: los {PLAZO_DIAS} días corridos "
                f"vencieron el {limite.strftime('%d/%m/%Y')} (Ley 24.240, art. 34)"
            ),
        )

    try:
        # Devolver stock
        for item in pedido.items:
            producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
            if producto:
                producto.stock += item.cantidad

        pedido.estado = "cancelado"

        solicitud = SolicitudRevocacion(
            codigo=generar_codigo(),
            pedido_id=pedido.id,
            usuario_id=usuario.id,
            creada_en=ahora,
        )
        db.add(solicitud)
        db.commit()
        db.refresh(solicitud)
        return solicitud

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la revocación",
        ) from exc
