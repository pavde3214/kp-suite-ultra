from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_db
from app.models import Material
from app.schemas.material import MaterialIn, MaterialOut
from app.services.csv_import import import_materials_csv

router = APIRouter(prefix="/api/v1/materials", tags=["materials"])

@router.get("", response_model=list[MaterialOut])
def list_materials(q: str | None = None, limit: int = 100, db: Session = Depends(get_db)):
    qset = select(Material)
    if q:
        like = f"%{q}%"
        qset = qset.where(Material.name.like(like) | Material.model.like(like))
    return db.execute(qset.limit(limit)).scalars().all()

@router.get("/suggest", response_model=list[MaterialOut])
def suggest_materials(q: str, db: Session = Depends(get_db)):
    like = f"%{q}%"
    qset = select(Material).where(Material.name.like(like) | Material.model.like(like)).limit(10)
    return db.execute(qset).scalars().all()

@router.post("", response_model=MaterialOut)
def create_material(payload: MaterialIn, db: Session = Depends(get_db)):
    m = Material(**payload.dict()); db.add(m); db.commit(); db.refresh(m); return m

@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    result = import_materials_csv(db, content)
    return {"status": "ok", **result}
