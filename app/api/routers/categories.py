from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models import Category
from app.schemas.category import CategoryIn, CategoryOut

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])

@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.execute(select(Category)).scalars().all()

@router.post("", response_model=CategoryOut)
def create_category(payload: CategoryIn, db: Session = Depends(get_db)):
    c = Category(**payload.dict()); db.add(c); db.commit(); db.refresh(c); return c
