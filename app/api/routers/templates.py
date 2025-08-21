from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
from app.api.deps import get_db
from app.models import TemplateRec
from app.config import TEMPLATES_DIR
from app.security.basic import admin_guard

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])

@router.get("")
def list_templates(db: Session = Depends(get_db)):
    rows = db.execute(select(TemplateRec)).scalars().all()
    return [{"id": r.id, "name": r.name, "path": Path(r.path).name, "uploaded_at": r.uploaded_at.isoformat()} for r in rows]

@router.post("/upload", dependencies=[Depends(admin_guard)])
async def upload_template(name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    path = TEMPLATES_DIR / name
    content = await file.read()
    path.write_bytes(content)
    row = db.execute(select(TemplateRec).where(TemplateRec.name==name)).scalar_one_or_none()
    if not row:
        row = TemplateRec(name=name, path=str(path)); db.add(row)
    else:
        row.path = str(path)
    db.commit()
    return {"status": "ok", "name": name}
