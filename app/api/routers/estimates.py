from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.api.deps import get_db
from app.models import Estimate, EstimateSection, EstimateItem
from app.schemas.estimate import EstimateIn, EstimateOut, SectionIn, SectionOut, ItemIn, ItemOut

router = APIRouter(prefix="/api/v1/estimates", tags=["estimates"])

@router.get("", response_model=list[EstimateOut])
def list_estimates(db: Session = Depends(get_db)):
    return db.execute(select(Estimate)).scalars().all()

@router.post("", response_model=EstimateOut)
def create_estimate(payload: EstimateIn, db: Session = Depends(get_db)):
    e = Estimate(**payload.dict()); db.add(e); db.commit(); db.refresh(e); return e

def _next_position_for_section(db: Session, section_id: int) -> str:
    sec = db.get(EstimateSection, section_id)
    if not sec: return ""
    try:
        sec_num = int((sec.position or "").split(".")[0])
    except:
        sections = db.execute(select(EstimateSection).where(EstimateSection.estimate_id==sec.estimate_id)).scalars().all()
        sec_num = sections.index(sec)+1
    count = db.execute(select(func.count(EstimateItem.id)).where(EstimateItem.section_id==section_id)).scalar_one()
    return f"{sec_num}.{count+1}"

@router.post("/sections", response_model=SectionOut)
def add_section(payload: SectionIn, db: Session = Depends(get_db)):
    count = db.execute(select(func.count(EstimateSection.id)).where(EstimateSection.estimate_id==payload.estimate_id)).scalar_one()
    s = EstimateSection(estimate_id=payload.estimate_id, title=payload.title, position=str(count+1))
    db.add(s); db.commit(); db.refresh(s); return s

@router.post("/items", response_model=ItemOut)
def add_item(payload: ItemIn, db: Session = Depends(get_db)):
    pos = _next_position_for_section(db, payload.section_id) if payload.section_id else None
    i = EstimateItem(**payload.dict(), position=pos); db.add(i); db.commit(); db.refresh(i); return i
