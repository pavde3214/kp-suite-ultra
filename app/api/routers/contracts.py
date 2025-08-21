from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import json
from datetime import date
from app.api.deps import get_db
from app.models import Customer, Owner, Estimate, Proposal, DocumentRec, ContractData
from app.services.numbering import generate_contract_number
from app.services.payments import estimate_totals, payment_schedule_100_70_30, proposal_totals
from app.services.docx_merge import render_docx
from app.services.spec_builder import build_spec_docx
from app.services.export_xlsx import export_spec_xlsx
from app.config import TEMPLATES_DIR, DOCS_DIR

router = APIRouter(prefix="/api/v1/contracts", tags=["contracts"])

def _fmt(x):
    try: return f"{float(x):,.0f}".replace(",", " ")
    except: return str(x)

def build_ctx(db: Session, customer_id: int, estimate_id: int | None, kp_id: int | None, overrides: dict | None = None):
    cust = db.get(Customer, customer_id)
    if not cust: raise HTTPException(404, "customer not found")
    owner = db.get(Owner, 1)
    if not owner:
        owner = Owner(id=1, display_name="Исполнитель"); db.add(owner); db.commit(); db.refresh(owner)
    est = db.get(Estimate, estimate_id) if estimate_id else None
    kp = db.get(Proposal, kp_id) if kp_id else None
    totals = {"equipment":0,"labor":0,"total":0}; sched = []
    if est:
        totals = estimate_totals(est); sched = payment_schedule_100_70_30(est)
    elif kp:
        totals = proposal_totals(kp); sched = [{"title":"Оплата по КП","amount":totals["total"]}]
    number = generate_contract_number(db)
    ctx = {
        "CONTRACT_NO": number, "CONTRACT_DATE": date.today().strftime("%d.%m.%Y"),
        "CUSTOMER_FIO": cust.fullname or "", "CUSTOMER_PASSPORT": cust.passport or "",
        "CUSTOMER_ADDR_REG": cust.address or "", "CUSTOMER_PHONE": cust.phone or "",
        "CUSTOMER_EMAIL": cust.email or "",
        "OBJECT_ADDR": (getattr(est, "site_address", None) if est else None) or (kp.site_address if kp else None) or (cust.address_object or ""),
        "EXECUTOR_FIO": owner.fullname or owner.display_name or "Исполнитель",
        "EXECUTOR_PASSPORT": owner.passport or "", "EXECUTOR_ADDR": owner.address or "",
        "EXECUTOR_PHONE": owner.phone or "", "EXECUTOR_EMAIL": owner.email or "",
        "EXECUTOR_INN": owner.inn or "", "EXECUTOR_OGRN": owner.ogrn or "",
        "SUM_EQUIP": _fmt(totals["equipment"]), "SUM_WORK":  _fmt(totals["labor"]),
        "SUM_TOTAL": _fmt(totals["total"]),
        "STAGE1": _fmt(sched[0]["amount"] if sched else 0),
        "STAGE2": _fmt(sched[1]["amount"] if len(sched)>1 else 0),
        "STAGE3": _fmt(sched[2]["amount"] if len(sched)>2 else 0),
        "DELIVERY_DAYS": overrides.get("DELIVERY_DAYS") if overrides else "",
        "INSTALL_DAYS": overrides.get("INSTALL_DAYS") if overrides else "",
        "WARRANTY_MONTHS": overrides.get("WARRANTY_MONTHS") if overrides else "",
        "KP_VALID_DAYS": overrides.get("KP_VALID_DAYS") if overrides else "",
        "PREPAYMENT_PCT": overrides.get("PREPAYMENT_PCT") if overrides else "",
    }
    if overrides:
        ctx.update({k: v for k, v in overrides.items() if k in ctx})
    return number, ctx, est, kp

@router.post("/create")
def create_contract(customer_id: int = Query(...), estimate_id: int | None = Query(None), kp_id: int | None = Query(None), db: Session = Depends(get_db)):
    number, ctx, est, kp = build_ctx(db, customer_id, estimate_id, kp_id)
    dog_tpl = TEMPLATES_DIR / "Договор.docx"
    if not dog_tpl.is_file(): raise HTTPException(400, "Нет шаблона Договор.docx в storage/templates/contracts")
    contract_out = DOCS_DIR / f"Договор_{number}.docx"
    render_docx(str(dog_tpl), str(contract_out), ctx)
    app1_out = None
    if est:
        app1_out = Path(build_spec_docx(est, number)); export_spec_xlsx(est, number)
    files = [contract_out] + ([app1_out] if app1_out else [])
    return {"contract_no": number, "files": [f.name for f in files if f], "download": [f"/files?path={f.name}" for f in files if f]}

@router.post("/save-context")
def save_context(customer_id: int, estimate_id: int | None = None, kp_id: int | None = None, overrides: dict | None = None, db: Session = Depends(get_db)):
    number, ctx, _, _ = build_ctx(db, customer_id, estimate_id, kp_id, overrides or {})
    row = ContractData(number=number, customer_id=customer_id, estimate_id=estimate_id, kp_id=kp_id, ctx_json=json.dumps(ctx, ensure_ascii=False))
    db.add(row); db.commit(); return {"status":"ok", "number": number}
