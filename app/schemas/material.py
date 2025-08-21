from pydantic import BaseModel
class MaterialIn(BaseModel):
    name: str
    model: str | None = None
    unit: str = "шт"
    price_material: float = 0.0
    price_labor: float = 0.0
    category_id: int | None = None
class MaterialOut(MaterialIn):
    id: int
    class Config: from_attributes = True
