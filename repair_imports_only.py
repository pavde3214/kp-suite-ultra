# -*- coding: utf-8 -*-
# Ремонтирует импорты в app/main.py: убирает битые строки и вставляет каноничный блок.
from pathlib import Path
import re

mp = Path("app/main.py")
src = mp.read_text(encoding="utf-8")

# Сохраняем возможную шебанг/кодировку вверху
lines = src.splitlines(keepends=True)
head = []
start = 0
for i, ln in enumerate(lines):
    if ln.startswith("#!") or ln.lower().startswith("# -*- coding"):
        head.append(ln)
        start = i + 1
    else:
        break
rest = "".join(lines[start:])

# Удаляем все существующие import'ы fastapi/sqlalchemy (включая битые)
rest = re.sub(r'(?m)^\s*from\s+fastapi(\.[\w\.]+)?\s+import[^\n]*\n', '', rest)
rest = re.sub(r'(?m)^\s*from\s+fastapi\s+import\s*$\n?', '', rest)  # полностью пустые строки "from fastapi import"
rest = re.sub(r'(?m)^\s*from\s+fastapi\.responses\s+import[^\n]*\n', '', rest)
rest = re.sub(r'(?m)^\s*from\s+sqlalchemy(\.[\w\.]+)?\s+import[^\n]*\n', '', rest)

# Каноничный блок импортов (без отступов, покрывает всё, что используем)
imports = (
    "from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, Body\n"
    "from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse\n"
    "from sqlalchemy import select, func, or_\n"
    "from sqlalchemy.orm import Session, joinedload\n"
)

mp.write_text("".join(head) + imports + rest, encoding="utf-8")
print("OK: imports repaired")
