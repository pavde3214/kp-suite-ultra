from pydantic import BaseModel, Field
class CustomerIn(BaseModel):
    fullname: str = Field(...)
    passport: str | None = None
    address: str | None = None
    address_object: str | None = None
    phone: str | None = None
    email: str | None = None
class CustomerOut(CustomerIn):
    id: int
    class Config: from_attributes = True
