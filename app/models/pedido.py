from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    estado = Column(String(20), nullable=False, default="pendiente", server_default="pendiente")
    total = Column(Numeric(12, 2), nullable=False, default=0)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    revocacion = relationship("SolicitudRevocacion", back_populates="pedido", uselist=False)


class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)  # foto del precio al comprar

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
