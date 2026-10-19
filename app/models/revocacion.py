from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db.database import Base


class SolicitudRevocacion(Base):
    __tablename__ = "solicitudes_revocacion"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, unique=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creada_en = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    from sqlalchemy.orm import relationship
    pedido = relationship("Pedido", back_populates="revocacion")
