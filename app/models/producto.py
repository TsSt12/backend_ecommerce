from sqlalchemy import Column, Float, Integer, String

from app.db.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    categoria = Column(String(60), nullable=False, index=True)
    precio_final = Column(Float, nullable=False)
    cuotas_cantidad = Column(Integer, nullable=False, default=1)
    cuotas_valor = Column(Float, nullable=False)
    garantia_meses = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    imagen_url = Column(String(255), nullable=True)    # Clase 10
