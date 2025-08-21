from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.api.deps import get_db
from app.models import Proposal, ProposalSection, ProposalItem
from app.schemas.proposal import ProposalIn, ProposalOut, PSectionIn, PSectionOut, PItemIn, PItemOut
from app.services.numbering import generate_proposal_number

router = APIRouter(prefix="/api/v1/proposals", tags=["proposals"])

@router.get("", response_model=list[ProposalOut])
def list_proposals(db: Session = Depends(get_db)):
    return db.execute(select(Proposal).order_by(Proposal.created_at.desc())).scalars().all()

@router.post("", response_model=ProposalOut)
def create_proposal(payload: ProposalIn, db: Session = Depends(get_db)):
    number = generate_proposal_number(db)
    p = Proposal(**payload.dict(), number=number)
    db.add(p); db.commit(); db.refresh(p); return p

def _next_position_for_section(db: Session, section_id: int) -> str:
    sec = db.get(ProposalSection, section_id)
    if not sec: return ""
    try:
        sec_num = int((sec.position or "").split(".")[0])
    except:
        sections = db.execute(select(ProposalSection).where(ProposalSection.proposal_id==sec.proposal_id)).scalars().all()
        sec_num = sections.index(sec)+1
    count = db.execute(select(func.count(ProposalItem.id)).where(ProposalItem.section_id==section_id)).scalar_one()
    return f"{sec_num}.{count+1}"

@router.post("/sections", response_model=PSectionOut)
def add_section(payload: PSectionIn, db: Session = Depends(get_db)):
    count = db.execute(select(func.count(ProposalSection.id)).where(ProposalSection.proposal_id==payload.proposal_id)).scalar_one()
    s = ProposalSection(proposal_id=payload.proposal_id, title=payload.title, position=str(count+1))
    db.add(s); db.commit(); db.refresh(s); return s

@router.post("/items", response_model=PItemOut)
def add_item(payload: PItemIn, db: Session = Depends(get_db)):
    pos = _next_position_for_section(db, payload.section_id) if payload.section_id else None
    i = ProposalItem(**payload.dict(), position=pos); db.add(i); db.commit(); db.refresh(i); return i
