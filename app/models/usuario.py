from sqlalchemy import Boolean, Column, DateTime, Integer, String, text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="customer", server_default="customer")

    # Ley 25.326 — consentimiento
    acepto_tratamiento = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    fecha_consentimiento = Column(DateTime(timezone=True), nullable=True)

    # Clase 9 — baja / anonimización
    activo = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    fecha_baja = Column(DateTime(timezone=True), nullable=True)

    pedidos = relationship("Pedido", back_populates="usuario")
