from pydantic import BaseModel
from typing import Optional
class EstimateIn(BaseModel):
    title: str = "Смета"
    customer_id: int
    site_address: Optional[str] = None
class EstimateOut(EstimateIn):
    id: int
    class Config: from_attributes = True
class SectionIn(BaseModel):
    estimate_id: int
    title: str
class SectionOut(SectionIn):
    id: int
    position: str | None = None
    class Config: from_attributes = True
class ItemIn(BaseModel):
    estimate_id: int
    section_id: int | None = None
    name: str
    item_type: str = "material"
    unit: str = "шт"
    qty: float = 1.0
    price_material: float = 0.0
    price_labor: float = 0.0
class ItemOut(ItemIn):
    id: int
    position: str | None = None
    class Config: from_attributes = True
