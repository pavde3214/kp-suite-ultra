from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, joinedload
from xhtml2pdf import pisa
from io import BytesIO

from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models import Customer, Estimate, EstimateSection, EstimateItem, Material, TemplateRec, DocumentRec, Owner, Proposal, ProposalSection, ProposalItem
from app.api.routers.customers import router as customers_router
from app.api.routers.estimates import router as estimates_router
from app.api.routers.materials import router as materials_router
from app.api.routers.categories import router as categories_router
from app.api.routers.contracts import router as contracts_router
from app.api.routers.templates import router as tpl_router
from app.api.routers.files import router as files_router
from app.api.routers.aihelper import router as ai_router
from app.api.routers.proposals import router as proposals_api
from app.config import STATIC_DIR, HTML_TPL_DIR, DOCS_DIR, TEMPLATES_DIR
from app.services.numbering import generate_proposal_number
from app.services.payments import estimate_totals, payment_schedule_100_70_30, proposal_totals
from app.services.docx_merge import render_docx

app = FastAPI(title="KP Suite ULTRA")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=HTML_TPL_DIR)

@app.on_event("startup")
def on_start(): init_db()

# API
app.include_router(files_router)
app.include_router(customers_router)
app.include_router(estimates_router)
app.include_router(materials_router)
app.include_router(categories_router)
app.include_router(contracts_router)
app.include_router(tpl_router)
app.include_router(ai_router)
app.include_router(proposals_api)

# UI
@app.get("/", response_class=HTMLResponse)
def index(request: Request): return templates.TemplateResponse("index.html", {"request": request})

@app.get("/customers", response_class=HTMLResponse)
def page_customers(request: Request):
    db: Session = SessionLocal()
    customers = db.execute(select(Customer)).scalars().all()
    db.close()
    return templates.TemplateResponse("customers.html", {"request": request, "customers": customers})

# ---------- CUSTOMER: create/save/full card ----------
@app.get("/customers/create", response_class=HTMLResponse)
def customers_create_get(request: Request):
    return RedirectResponse(url="/customers", status_code=303)

@app.post("/customers/create")
async def customers_create(fullname: str = Form(...), phone: str = Form(None), email: str = Form(None),
                           address: str = Form(None), address_object: str = Form(None), passport: str = Form(None)):
    db = SessionLocal()
    c = Customer(fullname=fullname, phone=phone, email=email, address=address, address_object=address_object, passport=passport)
    db.add(c); db.commit(); db.close()
    return RedirectResponse(url="/customers", status_code=303)

@app.get("/customers/card/{cid}", response_class=HTMLResponse)
def page_customer_card_full(request: Request, cid: int):
    db = SessionLocal()
    c = db.get(Customer, cid)
    if not c:
        db.close()
        return RedirectResponse(url="/customers", status_code=303)
    latest_kp = db.execute(select(Proposal).where(Proposal.customer_id==cid).order_by(Proposal.created_at.desc())).scalars().first()
    props = db.execute(select(Proposal).where(Proposal.customer_id==cid).order_by(Proposal.created_at.desc())).scalars().all()
    db.close()
    return templates.TemplateResponse("customer_card_full.html", {"request": request, "c": c, "latest_kp": latest_kp, "proposals": props})

@app.post("/customers/{cid}/save")
async def customers_save(cid: int, request: Request):
    form = await request.form()
    db = SessionLocal()
    c = db.get(Customer, cid)
    if not c:
        db.close()
        return RedirectResponse(url="/customers", status_code=303)
    c.fullname = form.get("fullname") or c.fullname
    c.passport = form.get("passport") or c.passport
    c.address = form.get("address") or c.address
    c.address_object = form.get("address_object") or c.address_object
    c.phone = form.get("phone") or c.phone
    c.email = form.get("email") or c.email
    db.add(c); db.commit(); db.close()
    return RedirectResponse(url=f"/customers/card/{cid}", status_code=303)

@app.post("/customers/{cid}/make-contract-latest-kp")
def make_contract_latest_kp(cid: int):
    db = SessionLocal()
    kp = db.execute(select(Proposal).where(Proposal.customer_id==cid).order_by(Proposal.created_at.desc())).scalars().first()
    db.close()
    if kp:
        return RedirectResponse(url=f"/contract/editor?customer_id={cid}&kp_id={kp.id}", status_code=303)
    else:
        return RedirectResponse(url=f"/contract/editor?customer_id={cid}", status_code=303)

# ---------- PROPOSALS (КП) UI ----------
@app.get("/proposals", response_class=HTMLResponse)
def list_proposals(request: Request):
    db: Session = SessionLocal()
    rows = db.execute(select(Proposal).order_by(Proposal.created_at.desc())).scalars().all()
    for r in rows: _ = r.customer
    db.close()
    return templates.TemplateResponse("proposals.html", {"request": request, "proposals": rows})

@app.get("/proposals/new", response_class=HTMLResponse)
def new_proposal_page(request: Request):
    return templates.TemplateResponse("proposal_new.html", {"request": request})

@app.post("/proposals/new")
async def new_proposal_create(request: Request):
    form = await request.form()
    customer_id = form.get("customer_id")
    db: Session = SessionLocal()
    from app.models import Customer, Proposal
    number = generate_proposal_number(db)
    # клиент
    c = None
    if customer_id:
        try: c = db.get(Customer, int(customer_id))
        except: c = None
    if not c:
        c = Customer(
            fullname=form.get("fullname") or "Новый клиент",
            phone=form.get("phone") or None,
            email=form.get("email") or None,
            address=form.get("address") or None,
            address_object=form.get("address_object") or None,
        )
        db.add(c); db.commit(); db.refresh(c)
    p = Proposal(
        customer_id=c.id, number=number,
        title=form.get("title") or "Коммерческое предложение",
        site_address=form.get("site_address") or c.address_object,
        header_html=form.get("header_html") or "<b>VENT•PRO HVAC</b>",
    )
    db.add(p); db.commit(); db.refresh(p); db.close()
    return RedirectResponse(url=f"/proposals/{p.id}/edit", status_code=303)

@app.get("/proposals/create")
def create_proposal_page(customer_id: int):
    db: Session = SessionLocal()
    number = generate_proposal_number(db)
    p = Proposal(customer_id=customer_id, number=number, title="Коммерческое предложение")
    db.add(p); db.commit(); db.refresh(p); db.close()
    return RedirectResponse(url=f"/proposals/{p.id}/edit", status_code=303)

@app.get("/proposals/{pid}/edit", response_class=HTMLResponse)
def edit_proposal(request: Request, pid: int):
    db: Session = SessionLocal()
    try:
        p = db.get(Proposal, pid)
        if not p:
            raise HTTPException(404, "Proposal not found")
        sections = db.execute(select(ProposalSection).where(ProposalSection.proposal_id==pid).order_by(ProposalSection.position)).scalars().all()
        items = db.execute(select(ProposalItem).where(ProposalItem.proposal_id==pid)).scalars().all()
        return templates.TemplateResponse("proposal_edit.html", {"request": request, "p": p, "sections": sections, "items": items})
    finally:
        db.close()

@app.post("/proposals/{pid}/save")
async def save_proposal(pid: int, request: Request):
    data = await request.json()
    db: Session = SessionLocal()
    try:
        p = db.get(Proposal, pid)
        if not p:
            raise HTTPException(404, "Proposal not found")
        p.title = data.get("title", p.title)
        p.site_address = data.get("site_address", p.site_address)
        p.header_html = data.get("header_html", p.header_html)
        db.add(p)
        db.commit()
        return {"status":"ok"}
    finally:
        db.close()

@app.get("/proposals/{pid}/print", response_class=HTMLResponse)
def print_proposal(request: Request, pid: int):
    db: Session = SessionLocal()
    p = db.execute(
        select(Proposal).options(joinedload(Proposal.customer)).where(Proposal.id == pid)
    ).scalar_one_or_none()
    if not p:
        db.close()
        raise HTTPException(404, "KP not found")
    sections = db.execute(
        select(ProposalSection).where(ProposalSection.proposal_id == pid).order_by(ProposalSection.position)
    ).scalars().all()
    items = db.execute(
        select(ProposalItem).where(ProposalItem.proposal_id == pid)
    ).scalars().all()
    # Ensure customer data is loaded before closing the session
    _ = p.customer.fullname if p.customer else None
    db.close()
    return templates.TemplateResponse("proposal_print.html", {"request": request, "p": p, "sections": sections, "items": items})

@app.get("/proposals/{pid}/pdf")
def pdf_proposal(request: Request, pid: int):
    import io
    db: Session = SessionLocal()
    p = db.execute(
        select(Proposal).options(joinedload(Proposal.customer)).where(Proposal.id == pid)
    ).scalar_one_or_none()
    if not p:
        db.close()
        raise HTTPException(404, "KP not found")
    sections = db.execute(
        select(ProposalSection).where(ProposalSection.proposal_id == pid).order_by(ProposalSection.position)
    ).scalars().all()
    items = db.execute(
        select(ProposalItem).where(ProposalItem.proposal_id == pid)
    ).scalars().all()
    # Ensure customer data is loaded before closing the session
    _ = p.customer.fullname if p.customer else None
    db.close()

    html = templates.env.get_template("proposal_print.html").render(
        {"request": request, "p": p, "sections": sections, "items": items}
    )
    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf, encoding='utf-8')
    buf.seek(0)
    headers = {"Content-Disposition": f'inline; filename="kp_{pid}.pdf"'}
    return StreamingResponse(buf, media_type="application/pdf", headers=headers)

# ---------- CONTRACT EDITOR & PRINT ----------
@app.get("/contract/editor", response_class=HTMLResponse)
def contract_editor(request: Request, customer_id: int, estimate_id: int | None = None, kp_id: int | None = None):
    from datetime import date
    ctx = {"CONTRACT_DATE": date.today().strftime("%d.%m.%Y")}
    return templates.TemplateResponse("contract_editor.html", {"request": request, "ctx": ctx})

@app.get("/print/contract", response_class=HTMLResponse)
def print_contract(request: Request, customer_id: int, estimate_id: int | None = None, kp_id: int | None = None,
                   CONTRACT_DATE: str | None = None, DELIVERY_DAYS: str | None = None, INSTALL_DAYS: str | None = None,
                   WARRANTY_MONTHS: str | None = None, KP_VALID_DAYS: str | None = None, PREPAYMENT_PCT: str | None = None):
    db: Session = SessionLocal()
    cust = db.get(Customer, customer_id)
    owner = db.get(Owner, 1) or Owner(id=1, display_name="Исполнитель"); db.add(owner); db.commit(); db.refresh(owner)
    est = db.get(Estimate, estimate_id) if estimate_id else None
    kp = db.get(Proposal, kp_id) if kp_id else None
    from app.services.numbering import generate_contract_number
    from app.services.payments import estimate_totals, proposal_totals
    totals = {"equipment":0,"labor":0,"total":0}
    if est: totals = estimate_totals(est)
    elif kp: totals = proposal_totals(kp)
    ctx = {
        "CONTRACT_NO": generate_contract_number(db),
        "CONTRACT_DATE": CONTRACT_DATE or "",
        "CUSTOMER_FIO": cust.fullname or "",
        "OBJECT_ADDR": (est.site_address if est else (kp.site_address if kp else "")) or cust.address_object or "",
        "EXECUTOR_FIO": owner.fullname or owner.display_name or "Исполнитель",
        "SUM_EQUIP": f"{totals['equipment']:,.0f}".replace(",", " "),
        "SUM_WORK": f"{totals['labor']:,.0f}".replace(",", " "),
        "SUM_TOTAL": f"{totals['total']:,.0f}".replace(",", " "),
        "STAGE1": "", "STAGE2": "", "STAGE3": "",
        "DELIVERY_DAYS": DELIVERY_DAYS, "INSTALL_DAYS": INSTALL_DAYS, "WARRANTY_MONTHS": WARRANTY_MONTHS,
        "KP_VALID_DAYS": KP_VALID_DAYS, "PREPAYMENT_PCT": PREPAYMENT_PCT,
    }
    db.close()
    return templates.TemplateResponse("print_contract.html", {"request": request, "ctx": ctx})

@app.get("/contract/docx")
def contract_docx(customer_id: int, estimate_id: int | None = None, kp_id: int | None = None, **kwargs):
    db: Session = SessionLocal()
    try:
        from app.api.routers.contracts import build_ctx
        number, ctx, _, _ = build_ctx(db, customer_id, estimate_id, kp_id, kwargs)
        tpl = TEMPLATES_DIR / "Договор.docx"
        if not tpl.is_file():
            raise HTTPException(400, "Нет шаблона Договор.docx")
        out = DOCS_DIR / f"Договор_{number}.docx"
        render_docx(str(tpl), str(out), ctx)
        return FileResponse(str(out), filename=out.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    finally:
        db.close()

# ---------- MATERIALS UI ----------
@app.get("/materials", response_class=HTMLResponse)
def materials_page(request: Request):
    return templates.TemplateResponse("materials.html", {"request": request})

# ---------- TEMPLATES UI ----------
@app.get("/templates", response_class=HTMLResponse)
def page_templates(request: Request):
    return templates.TemplateResponse("templates.html", {"request": request})

# ---------- Documents UI ----------
@app.get("/documents", response_class=HTMLResponse)
def page_documents(request: Request):
    db: Session = SessionLocal()
    docs = db.execute(select(DocumentRec).order_by(DocumentRec.created_at.desc())).scalars().all()
    db.close()
    return templates.TemplateResponse("documents.html", {"request": request, "docs": docs})

@app.get("/health")
def health(): return {"status": "ok"}


@app.post("/materials/create")
async def materials_create(name: str = Form(...), model: str = Form(None), unit: str = Form("шт"),
                           price_material: str = Form("0"), price_labor: str = Form("0")):
    db: Session = SessionLocal()
    m = Material(
        name=name, model=model or None, unit=unit or "шт",
        price_material=float(price_material or 0),
        price_labor=float(price_labor or 0)
    )
    db.add(m); db.commit(); db.close()
    return RedirectResponse(url="/materials", status_code=303)


@app.post("/materials/import")
async def materials_import(file: UploadFile = File(...)):
    import csv, io
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("cp1251", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))

    db: Session = SessionLocal()
    created = 0
    for row in reader:
        name = (row.get('name') or row.get('Наименование') or '').strip()
        if not name: 
            continue
        m = Material(
            name=name,
            model=(row.get('model') or row.get('Модель') or '').strip() or None,
            unit=(row.get('unit') or row.get('Ед') or 'шт').strip() or 'шт',
            price_material=float((row.get('price_material') or row.get('ЦенаМат') or 0) or 0),
            price_labor=float((row.get('price_labor') or row.get('ЦенаМонтаж') or 0) or 0),
        )
        db.add(m); created += 1
    db.commit(); db.close()
    return RedirectResponse(url="/materials", status_code=303)


@app.post("/templates/upload")
async def templates_upload(name: str = Form(...), file: UploadFile = File(...)):
    from app.config import TEMPLATES_DIR
    from app.models import TemplateRec
    path = TEMPLATES_DIR / name
    content = await file.read()
    path.write_bytes(content)

    db: Session = SessionLocal()
    row = db.execute(select(TemplateRec).where(TemplateRec.name==name)).scalar_one_or_none()
    if not row:
        row = TemplateRec(name=name, path=str(path)); db.add(row)
    else:
        row.path = str(path)
    db.commit(); db.close()
    return RedirectResponse(url="/templates", status_code=303)


@app.post("/api/v1/proposals/sections")
async def api_create_section(payload: dict = Body(...)):
    pid = int(payload.get("proposal_id"))
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(422, "Title is required")
    db: Session = SessionLocal()
    last_pos = db.execute(
        select(func.coalesce(func.max(ProposalSection.position), 0)).where(ProposalSection.proposal_id == pid)
    ).scalar_one()
    sec = ProposalSection(proposal_id=pid, title=title, position=int(last_pos)+1)
    db.add(sec); db.commit(); db.refresh(sec); db.close()
    return JSONResponse({"id": sec.id, "position": sec.position, "title": sec.title})


@app.post("/api/v1/proposals/items")
async def api_create_item(payload: dict = Body(...)):
    pid = int(payload.get("proposal_id"))
    sec_id = int(payload.get("section_id"))
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(422, "Name is required")
    note = (payload.get("note") or None)
    unit = (payload.get("unit") or "шт")
    qty = float(payload.get("qty") or 1)
    price = float(payload.get("price") or 0)
    price_labor = float(payload.get("price_labor") or 0)

    db: Session = SessionLocal()
    last_pos = db.execute(
        select(func.coalesce(func.max(ProposalItem.position), 0)).where(ProposalItem.section_id == sec_id)
    ).scalar_one()
    item = ProposalItem(
        proposal_id=pid, section_id=sec_id, position=int(last_pos)+1,
        name=name, note=note, unit=unit, qty=qty, price=price, price_labor=price_labor
    )
    db.add(item); db.commit(); db.refresh(item); db.close()
    return JSONResponse({"id": item.id, "position": item.position})


@app.get("/api/v1/materials")
def api_materials(q: str = ""):
    db: Session = SessionLocal()
    query = select(Material).order_by(Material.id.desc())
    if q:
        like = f"%{q}%"
        query = query.where(or_(Material.name.ilike(like), Material.model.ilike(like)))
    rows = db.execute(query).scalars().all()
    data = [{
        "id": r.id, "name": r.name, "model": r.model,
        "unit": r.unit, "price_material": r.price_material, "price_labor": r.price_labor
    } for r in rows]
    db.close()
    return JSONResponse(data)
