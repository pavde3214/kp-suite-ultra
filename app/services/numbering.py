from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Sequence
from app.config import CONTRACT_NUMBER_MASK, PROPOSAL_NUMBER_MASK

def next_seq(db: Session, name: str) -> int:
    row = db.execute(select(Sequence).where(Sequence.name==name)).scalar_one_or_none()
    if not row:
        row = Sequence(name=name, last=0); db.add(row); db.commit(); db.refresh(row)
    row.last += 1; db.add(row); db.commit(); db.refresh(row); return row.last

def generate_contract_number(db: Session) -> str:
    now = datetime.now(); seq = next_seq(db, "DOG")
    return CONTRACT_NUMBER_MASK.replace("{YYYY}", f"{now.year}").replace("{SEQ:04d}", f"{seq:04d}")

def generate_proposal_number(db: Session) -> str:
    now = datetime.now(); seq = next_seq(db, "KP")
    return PROPOSAL_NUMBER_MASK.replace("{YYYY}", f"{now.year}").replace("{SEQ:04d}", f"{seq:04d}")
