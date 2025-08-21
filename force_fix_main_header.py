# -*- coding: utf-8 -*-
# Жёстко чинит шапку импортов в app/main.py и удаляет "обрывки" import-строк.
from pathlib import Path
import re

mp = Path("app/main.py")
src = mp.read_text(encoding="utf-8")

# 1) Отделим возможный shebang/кодировку вверху
lines = src.splitlines(keepends=True)
prefix = []
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith("#!") or ln.lower().startswith("# -*- coding"):
        prefix.append(ln)
        i += 1
        continue
    break
rest = "".join(lines[i:])

# 2) Удалим все import-строки fastapi/sqlalchemy, чтобы не было дублей/обрывков
patterns = [
    r'(?m)^\s*from\s+fastapi(\.[\w\.]+)?\s+import[^\n]*\n',
    r'(?m)^\s*from\s+fastapi\s+import\s*$\n?',                 # «обрывок» из нескольких слов
    r'(?m)^\s*from\s+fastapi\.responses\s+import[^\n]*\n',
    r'(?m)^\s*from\s+sqlalchemy(\.[\w\.]+)?\s+import[^\n]*\n',
]
for p in patterns:
    rest = re.sub(p, '', rest)

# 3) На всякий случай удалим одиночные "обрывки" вида:
#    FastAPI, Request, UploadFile, ...
rest = re.sub(
    r'(?m)^\s*(FastAPI|Request|UploadFile|File|Form|Depends|HTTPException|Body)(\s*,\s*\w+)*\s*$\n?',
    '',
    rest
)

# 4) Вставим каноничный блок импортов без отступов
imports = (
    "from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, Body\n"
    "from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse\n"
    "from sqlalchemy import select, func, or_\n"
    "from sqlalchemy.orm import Session, joinedload\n"
)

fixed = "".join(prefix) + imports + rest
mp.write_text(fixed, encoding="utf-8")
print("OK: main.py header imports repaired.")
