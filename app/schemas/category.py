from pydantic import BaseModel
class CategoryIn(BaseModel):
    name: str
    parent_id: int | None = None
    kind: str = "materials"
class CategoryOut(CategoryIn):
    id: int
    class Config: from_attributes = True
