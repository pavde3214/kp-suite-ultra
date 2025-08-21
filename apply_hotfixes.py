# -*- coding: utf-8 -*-
# Горячие фиксы: 500 в редакторе КП, 422 в договоре, 404 в загрузке шаблонов и создании материалов.
# Запуск:  .venv\Scripts\python.exe apply_hotfixes.py
from pathlib import Path
import re, textwrap

BASE = Path(__file__).resolve().parent

def write(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    print("wrote:", rel)

def patch(path, replacer):
    p = BASE / path
    s = p.read_text(encoding="utf-8")
    ns = replacer(s)
    if ns != s:
        p.write_text(ns, encoding="utf-8")
        print("patched:", path)
    else:
        print("no changes:", path)

# --- 1) contract_editor.html: убираем проброс "null" в query ---
def fix_contract_editor_html(_s):
    s = _s
    s = re.sub(
        r"function reloadPreview\(\)\{[\s\S]*?\}",
        """
function reloadPreview(){
  const urlParams = new URLSearchParams(window.location.search);
  const customer_id = urlParams.get('customer_id');
  const estimate_id = urlParams.get('estimate_id');
  const kp_id = urlParams.get('kp_id');

  const q = new URLSearchParams();
  if (customer_id) q.set('customer_id', customer_id);
  if (estimate_id && estimate_id !== 'null' && estimate_id !== '') q.set('estimate_id', estimate_id);
  if (kp_id && kp_id !== 'null' && kp_id !== '') q.set('kp_id', kp_id);

  const fields = ['CONTRACT_DATE','DELIVERY_DAYS','INSTALL_DAYS','WARRANTY_MONTHS','KP_VALID_DAYS','PREPAYMENT_PCT'];
  for (const f of fields){
    const v = document.getElementById(f)?.value ?? '';
    if (v !== '') q.set(f, v);
  }
  document.getElementById('preview').src = '/print/contract?' + q.toString();
  document.getElementById('btn-docx').href = '/contract/docx?' + q.toString();
}
        """.strip(),
        s, flags=re.M
    )
    return s

patch("app/web/templates/contract_editor.html", fix_contract_editor_html)

# --- 2) main.py: правим редактор КП (joinedload customer), добиваем недостающие UI-роуты ---

def fix_main_py(_s: str) -> str:
    s = _s

    # импорт joinedload (если вдруг нет)
    if "from sqlalchemy.orm import joinedload" not in s:
        s = s.replace(
            "from sqlalchemy.orm import Session",
            "from sqlalchemy.orm import Session, joinedload"
        )

    # заменить edit_proposal на версию с joinedload и безопасным закрытием сессии
    s = re.sub(
        r'@app\.get\("/proposals/\{pid\}/edit".*?def edit_proposal\([^\)]*\):[\s\S]*?return templates\.TemplateResponse\("proposal_edit\.html".*?\)\n',
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
            # доступимся к полю, чтобы точно прогрузить до закрытия сессии
            _ = p.customer.fullname if p.customer else None
            db.close()
            return templates.TemplateResponse("proposal_edit.html", {"request": request, "p": p, "sections": sections, "items": items})
        """),
        s, flags=re.M
    )

    # добавить POST /materials/create (UI-форма из /materials)
    if 'def materials_create(' not in s:
        s += textwrap.dedent("""

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
        """)

    # добавить POST /materials/import (UI)
    if 'def materials_import(' not in s:
        s += textwrap.dedent("""

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
        """)

    # добавить POST /templates/upload (UI-форма на /templates)
    if 'def templates_upload(' not in s:
        s += textwrap.dedent("""

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
        """)

    return s

patch("app/main.py", fix_main_py)

print("== HOTFIXES APPLIED ==")
print("Теперь перезапустите сервер: run_kp.bat")
