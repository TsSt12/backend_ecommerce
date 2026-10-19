from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    """Datos que el cliente puede enviar para crear o actualizar un producto."""
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=60)
    precio_final: float = Field(gt=0)
    cuotas_cantidad: int = Field(ge=1)
    cuotas_valor: float = Field(gt=0)
    garantia_meses: int = Field(ge=0)
    stock: int = Field(ge=0)


class ProductoOut(ProductoCreate):
    """Lo que la API devuelve: incluye id e imagen_url."""
    id: int
    imagen_url: str | None = None
    model_config = {"from_attributes": True}
