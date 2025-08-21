# -*- coding: utf-8 -*-
# Добавляет недостающие импорты CORSMiddleware/StaticFiles в app/main.py
from pathlib import Path
import re

p = Path("app/main.py")
src = p.read_text(encoding="utf-8")

def ensure_line(s: str, needle: str, insert_after_first_import: bool = True) -> str:
    if needle in s:
        return s
    lines = s.splitlines()
    # найдём первую строку, начинающуюся с "from" или "import" — туда подставим импорт
    idx = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith(("from ", "import ")):
            idx = i + 1
            break
    lines.insert(idx, needle)
    return "\n".join(lines) + ("\n" if not s.endswith("\n") else "")

src = ensure_line(src, "from fastapi.middleware.cors import CORSMiddleware")
src = ensure_line(src, "from fastapi.staticfiles import StaticFiles")

p.write_text(src, encoding="utf-8")
print("OK: CORSMiddleware/StaticFiles imports ensured.")
