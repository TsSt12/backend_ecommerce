from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ItemIn(BaseModel):
    """Un ítem del carrito: solo producto + cantidad. El precio lo pone el servidor."""
    producto_id: int
    cantidad: int = Field(ge=1)

    model_config = {"extra": "forbid"}   # si el cliente manda "precio": 1 → 422


class PedidoCreate(BaseModel):
    """Lo que el cliente envía para crear un pedido.
    No incluye total, precio ni usuario_id: los calcula el servidor."""
    items: list[ItemIn] = Field(min_length=1)

    model_config = {"extra": "forbid"}


class ItemOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    model_config = {"from_attributes": True}


class PedidoOut(BaseModel):
    id: int
    estado: str
    total: Decimal
    creado_en: datetime
    items: list[ItemOut]
    model_config = {"from_attributes": True}
