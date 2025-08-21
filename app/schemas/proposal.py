from pydantic import BaseModel
from typing import Optional
class ProposalIn(BaseModel):
    title: str = "Коммерческое предложение"
    customer_id: int
    site_address: Optional[str] = None
    header_html: Optional[str] = ""
class ProposalOut(ProposalIn):
    id: int
    number: str | None = None
    class Config: from_attributes = True
class PSectionIn(BaseModel):
    proposal_id: int
    title: str
class PSectionOut(PSectionIn):
    id: int
    position: str | None = None
    class Config: from_attributes = True
class PItemIn(BaseModel):
    proposal_id: int
    section_id: int | None = None
    name: str
    note: str | None = None
    unit: str = "шт"
    qty: float = 1.0
    price: float = 0.0
    price_labor: float = 0.0
class PItemOut(PItemIn):
    id: int
    position: str | None = None
    class Config: from_attributes = True
