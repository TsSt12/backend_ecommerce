from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pedido import ItemPedido, Pedido
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.schemas.pedido import PedidoCreate


def crear_pedido(db: Session, usuario: Usuario, datos: PedidoCreate) -> Pedido:
    """
    Transacción completa de checkout:
    1. Verifica existencia de todos los productos.
    2. Verifica stock suficiente.
    3. Descuenta stock, congela precio_unitario y calcula total en el servidor.
    Todo con rollback si algo falla.
    """
    try:
        items_orm = []
        total = Decimal("0")

        for item_in in datos.items:
            producto = db.query(Producto).filter(Producto.id == item_in.producto_id).first()
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto {item_in.producto_id} no encontrado",
                )
            if producto.stock < item_in.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}': "
                        f"disponible {producto.stock}, pedido {item_in.cantidad}"
                    ),
                )
            # Descontar stock
            producto.stock -= item_in.cantidad
            precio = Decimal(str(producto.precio_final))
            total += precio * item_in.cantidad
            items_orm.append(
                ItemPedido(
                    producto_id=item_in.producto_id,
                    cantidad=item_in.cantidad,
                    precio_unitario=precio,
                )
            )

        pedido = Pedido(usuario_id=usuario.id, total=total, items=items_orm)
        db.add(pedido)
        db.commit()
        db.refresh(pedido)
        return pedido

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al crear el pedido",
        ) from exc


def obtener_pedido(db: Session, pedido_id: int, usuario: Usuario) -> Pedido:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    # 404 incluso si el pedido existe pero es ajeno: no revelar que existe (Clase 8)
    if not pedido or (pedido.usuario_id != usuario.id and usuario.rol != "admin"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pedido no encontrado")
    return pedido


def listar_mis_pedidos(db: Session, usuario: Usuario) -> list[Pedido]:
    return (
        db.query(Pedido)
        .filter(Pedido.usuario_id == usuario.id)
        .order_by(Pedido.creado_en.desc())
        .all()
    )
