from datetime import datetime

from pydantic import BaseModel


class RevocacionOut(BaseModel):
    codigo: str
    pedido_id: int
    creada_en: datetime
    model_config = {"from_attributes": True}
