# -*- coding: utf-8 -*-
# Чинит импорты в app/main.py + обновляет print/pdf КП на joinedload
from pathlib import Path
import re, textwrap

BASE = Path(__file__).resolve().parent
MP = BASE / "app" / "main.py"

src = MP.read_text(encoding="utf-8")

# 1) Удаляем битые строки "from fastapi import" без содержимого
src = re.sub(r'(?m)^\s*from\s+fastapi\s+import\s*$\n?', '', src)

# 2) Убедимся, что есть каноничные импорты (добавим в самое начало, если их нет)
canon_imports = textwrap.dedent("""
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, joinedload
""").lstrip("\n")

if "from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, Body" not in src:
    src = canon_imports + "\n" + src

# 3) Переопределяем /proposals/{pid}/print c joinedload(customer)
pattern_print = re.compile(
    r'@app\.get\("/proposals/\{pid\}/print"[^\)]*\)\s+def\s+print_proposal\([^\)]*\):[\s\S]*?(?=\n@app\.|$)',
    re.M
)
body_print = textwrap.dedent(r"""
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
""").strip()

if pattern_print.search(src):
    src = pattern_print.sub(body_print, src)
else:
    # если вдруг не найден — просто добавим реализацию (не мешает существующей)
    src += "\n\n" + body_print + "\n"

# 4) Переопределяем /proposals/{pid}/pdf (рендер HTML -> PDF), с joinedload(customer)
pattern_pdf = re.compile(
    r'@app\.get\("/proposals/\{pid\}/pdf"[^\)]*\)\s+def\s+pdf_proposal\([^\)]*\):[\s\S]*?(?=\n@app\.|$)',
    re.M
)
body_pdf = textwrap.dedent(r"""
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
""").strip()

if pattern_pdf.search(src):
    src = pattern_pdf.sub(body_pdf, src)
else:
    src += "\n\n" + body_pdf + "\n"

MP.write_text(src, encoding="utf-8")
print("OK: imports fixed, print/pdf routes updated.")
