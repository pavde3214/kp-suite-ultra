# -*- coding: utf-8 -*-
# Полный фикс: редактор и печать КП (joinedload), API сметы и каталог, страховки в шаблонах.
# Запуск:  .venv\Scripts\python.exe apply_full_fix_kp_catalog.py
from pathlib import Path
import re, textwrap

BASE = Path(__file__).resolve().parent

def patch(path, fn):
    p = BASE / path
    s = p.read_text(encoding="utf-8")
    ns = fn(s)
    if ns != s:
        p.write_text(ns, encoding="utf-8")
        print("patched:", path)
    else:
        print("no changes:", path)

def ensure_inject(s: str, marker_after: str, inject: str) -> str:
    if inject.strip() in s:
        return s
    idx = s.find(marker_after)
    if idx == -1:
        # если маркер не нашли — просто prepend
        return inject + "\n" + s
    return s[:idx+len(marker_after)] + "\n" + inject + "\n" + s[idx+len(marker_after):]

# ---------- main.py ----------
def fix_main_py(_s: str) -> str:
    s = _s

    # 0) гарантируем импорты
    extra_imports = textwrap.dedent("""
    from fastapi import Body
    from fastapi.responses import JSONResponse, StreamingResponse
    from sqlalchemy import func, or_
    from sqlalchemy.orm import joinedload
    """).strip()

    # Вставим после первых импортов FastAPI/SQLAlchemy (или в начало, если не найдёт)
    s = ensure_inject(s, "import", extra_imports)

    # 1) /proposals/{pid}/edit — жадная загрузка customer
    if '@app.get("/proposals/{pid}/edit' in s:
        s = re.sub(
            r'@app\.get\("/proposals/\{pid\}/edit".*?def edit_proposal\([^\)]*\):[\s\S]*?return templates\.TemplateResponse\("proposal_edit\.html",[^\)]+\)\n',
            textwrap.dedent(r"""
            @app.get("/proposals/{pid}/edit", response_class=HTMLResponse)
            def edit_proposal(request: Request, pid: int):
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
                _ = p.customer.fullname if p.customer else None  # принудительно загружаем до закрытия сессии
                db.close()
                return templates.TemplateResponse("proposal_edit.html", {"request": request, "p": p, "sections": sections, "items": items})
            """),
            s, flags=re.M
        )

    # 2) /proposals/{pid}/print — тоже с joinedload
    if '@app.get("/proposals/{pid}/print' in s:
        s = re.sub(
            r'@app\.get\("/proposals/\{pid\}/print".*?def print_proposal\([^\)]*\):[\s\S]*?return templates\.TemplateResponse\("proposal_print\.html",[^\)]+\)\n',
            textwrap.dedent(r"""
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
                _ = p.customer.fullname if p.customer else None
                db.close()
                return templates.TemplateResponse("proposal_print.html", {"request": request, "p": p, "sections": sections, "items": items})
            """),
            s, flags=re.M
        )

    # 3) /proposals/{pid}/pdf — рендерим HTML строкой и конвертируем в PDF
    if '@app.get("/proposals/{pid}/pdf' in s:
        s = re.sub(
            r'@app\.get\("/proposals/\{pid\}/pdf".*?def pdf_proposal\([^\)]*\):[\s\S]*?\n(?=@app|get\(|$)',
            textwrap.dedent(r"""
            @app.get("/proposals/{pid}/pdf")
            def pdf_proposal(request: Request, pid: int):
                from xhtml2pdf import pisa
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
            """),
            s, flags=re.M
        )

    # 4) API: сохранить заголовок/адрес/шапку КП
    if 'def save_proposal(' not in s:
        s += textwrap.dedent("""

        @app.post("/proposals/{pid}/save")
        async def save_proposal(pid: int, payload: dict = Body(...)):
            db: Session = SessionLocal()
            p = db.get(Proposal, pid)
            if not p:
                db.close()
                raise HTTPException(404, "KP not found")
            p.title = payload.get("title") or p.title
            p.site_address = payload.get("site_address") or p.site_address
            p.header_html = payload.get("header_html") or p.header_html
            db.commit(); db.close()
            return JSONResponse({"ok": True})
        """)

    # 5) API: создать раздел сметы
    if '"/api/v1/proposals/sections"' not in s:
        s += textwrap.dedent("""

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
        """)

    # 6) API: создать позицию сметы
    if '"/api/v1/proposals/items"' not in s:
        s += textwrap.dedent("""

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
        """)

    # 7) API: поиск по каталогу материалов
    if '"/api/v1/materials"' not in s:
        s += textwrap.dedent("""

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
        """)

    return s

patch("app/main.py", fix_main_py)

# ---------- proposal_edit.html: защита, если у КП нет customer ----------
def fix_proposal_edit_html(_s: str) -> str:
    s = _s
    s = s.replace(
        'value="{{ p.site_address or p.customer.address_object or \'\' }}"',
        'value="{{ p.site_address or (p.customer.address_object if p.customer else \'\') }}"'
    )
    return s

patch("app/web/templates/proposal_edit.html", fix_proposal_edit_html)

# ---------- proposal_print.html: тоже страхуем доступ к p.customer ----------
def fix_proposal_print_html(_s: str) -> str:
    s = _s
    s = s.replace("Клиент: {{ p.customer.fullname }}", "Клиент: {{ p.customer.fullname if p.customer else '' }}")
    s = s.replace("Контакты: {{ p.customer.phone or \"\" }} {{ p.customer.email or \"\" }}",
                  "Контакты: {{ (p.customer.phone if p.customer else '') or '' }} {{ (p.customer.email if p.customer else '') or '' }}")
    s = s.replace("{{ p.site_address or p.customer.address_object or '' }}",
                  "{{ p.site_address or (p.customer.address_object if p.customer else '') }}")
    return s

patch("app/web/templates/proposal_print.html", fix_proposal_print_html)

print("=== FULL KP & CATALOG FIX APPLIED ===")
print("Перезапустите сервер: run_kp.bat")
