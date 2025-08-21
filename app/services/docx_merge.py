from docx import Document
from pathlib import Path
import os
def _replace_in_par(par, mapping: dict):
    text = "".join(r.text for r in par.runs); changed = False
    for k, v in mapping.items():
        ph = f"[[{k}]]"
        if ph in text: text = text.replace(ph, str(v)); changed = True
    if changed:
        for _ in range(len(par.runs)-1): par.runs[-1].clear()
        par.runs[0].text = text
def _walk(cell_or_doc, mapping: dict):
    for p in getattr(cell_or_doc, "paragraphs", []): _replace_in_par(p, mapping)
    for t in getattr(cell_or_doc, "tables", []):
        for row in t.rows:
            for cell in row.cells: _walk(cell, mapping)
def render_docx(src_path: str, dst_path: str, mapping: dict) -> str:
    doc = Document(src_path); _walk(doc, mapping)
    Path(os.path.dirname(dst_path)).mkdir(parents=True, exist_ok=True)
    doc.save(dst_path); return dst_path
