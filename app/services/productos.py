from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.producto import Producto
from app.schemas.producto import ProductoCreate


# ---------------------------------------------------------------------------
# Crear
# ---------------------------------------------------------------------------
def crear_producto(db: Session, datos: ProductoCreate) -> Producto:
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


# ---------------------------------------------------------------------------
# Listar (con filtros y paginación)
# ---------------------------------------------------------------------------
def listar_productos(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    nombre: str | None = None,
    precio_max: float | None = None,
    categoria: str | None = None,
) -> list[Producto]:
    consulta = db.query(Producto)
    if nombre:
        consulta = consulta.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if precio_max is not None:
        consulta = consulta.filter(Producto.precio_final <= precio_max)
    if categoria:
        consulta = consulta.filter(func.lower(Producto.categoria) == categoria.lower())
    return consulta.order_by(Producto.id).offset(skip).limit(limit).all()


# ---------------------------------------------------------------------------
# Detalle por id
# ---------------------------------------------------------------------------
def obtener_producto(db: Session, producto_id: int) -> Producto:
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Producto {producto_id} no encontrado")
    return producto


# ---------------------------------------------------------------------------
# Actualizar
# ---------------------------------------------------------------------------
def actualizar_producto(db: Session, producto_id: int, datos: ProductoCreate) -> Producto:
    producto = obtener_producto(db, producto_id)
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


# ---------------------------------------------------------------------------
# Eliminar
# ---------------------------------------------------------------------------
def eliminar_producto(db: Session, producto_id: int) -> None:
    producto = obtener_producto(db, producto_id)
    db.delete(producto)
    db.commit()


# ---------------------------------------------------------------------------
# Actualizar solo la imagen
# ---------------------------------------------------------------------------
def actualizar_imagen(db: Session, producto_id: int, imagen_url: str) -> Producto:
    producto = obtener_producto(db, producto_id)
    producto.imagen_url = imagen_url
    db.commit()
    db.refresh(producto)
    return producto
