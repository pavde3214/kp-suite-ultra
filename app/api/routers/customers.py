from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models import Customer
from app.schemas.customer import CustomerIn, CustomerOut

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])

@router.get("", response_model=list[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.execute(select(Customer)).scalars().all()

@router.post("", response_model=CustomerOut)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
    c = Customer(**payload.dict()); db.add(c); db.commit(); db.refresh(c); return c
