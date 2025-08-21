@echo off
setlocal EnableExtensions
cd /d %~dp0

REM ================= USER SETTINGS =================
REM Впишите ссылку на пустой удалённый репозиторий (HTTPS или SSH),
REM или оставьте пустым, чтобы пропустить push.
set "REMOTE_URL="
REM =================================================

if not exist scripts mkdir scripts

REM --- .gitignore ---
powershell -NoProfile -Command "@'
# --- Python / FastAPI ---
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg-info/
*.log

# venv (локальное окружение)
.venv/
venv/
ENV/
env/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db

# Бинарные сборки/кэш
dist/
build/
*.bak

# Локальные БД/артефакты (если нужно коммитить *.db — уберите строку)
*.db
*.sqlite3

# Секреты/конфиги
.env
.env.*
!env.example

# Временные/загружаемые файлы
uploads/
tmp/
temp/

# PDF/печать (генерируемые)
*.pdf
'@ | Set-Content -Encoding UTF8 .gitignore"

REM --- .gitattributes ---
powershell -NoProfile -Command "@'
* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
'@ | Set-Content -Encoding UTF8 .gitattributes"

REM --- scripts\force_fix_main_header.py ---
powershell -NoProfile -Command "@'
# -*- coding: utf-8 -*-
# Жёстко чинит шапку импортов в app/main.py (убирает обрывки и дубли)
from pathlib import Path
import re

mp = Path(\"app/main.py\")
src = mp.read_text(encoding=\"utf-8\")

# Сохраним возможную шебанг/кодировку
lines = src.splitlines(keepends=True)
prefix = []
i = 0
while i < len(lines):
    ln = lines[i]
    if ln.startswith(\"#!\") or ln.lower().startswith(\"# -*- coding\"):
        prefix.append(ln)
        i += 1
        continue
    break
rest = \"\".join(lines[i:])

# Удаляем все import-строки fastapi/sqlalchemy (включая битые)
patterns = [
    r'(?m)^\\s*from\\s+fastapi(\\.[\\w\\.]+)?\\s+import[^\\n]*\\n',
    r'(?m)^\\s*from\\s+fastapi\\s+import\\s*$\\n?',
    r'(?m)^\\s*from\\s+fastapi\\.responses\\s+import[^\\n]*\\n',
    r'(?m)^\\s*from\\s+sqlalchemy(\\.[\\w\\.]+)?\\s+import[^\\n]*\\n',
]
for p in patterns:
    rest = re.sub(p, '', rest)

# Удаляем висячие строки типа: \"FastAPI, Request, UploadFile, ...\"
rest = re.sub(
    r'(?m)^\\s*(FastAPI|Request|UploadFile|File|Form|Depends|HTTPException|Body)(\\s*,\\s*\\w+)*\\s*$\\n?',
    '',
    rest
)

imports = (
    \"from fastapi import FastAPI, Request, UploadFile, File, Form, Depends, HTTPException, Body\\n\"
    \"from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse\\n\"
    \"from sqlalchemy import select, func, or_\\n\"
    \"from sqlalchemy.orm import Session, joinedload\\n\"
)

mp.write_text(\"\".join(prefix) + imports + rest, encoding=\"utf-8\")
print(\"OK: main.py header imports repaired.\")
'@ | Set-Content -Encoding UTF8 scripts\force_fix_main_header.py"

REM --- scripts\fix_cors_import.py ---
powershell -NoProfile -Command "@'
# -*- coding: utf-8 -*-
# Добавляет импорты CORSMiddleware/StaticFiles в app/main.py, если их нет
from pathlib import Path

p = Path(\"app/main.py\")
src = p.read_text(encoding=\"utf-8\")

def ensure_line(s: str, needle: str) -> str:
    if needle in s:
        return s
    lines = s.splitlines()
    # вставим после первого import/from
    idx = 0
    for i, ln in enumerate(lines):
        if ln.strip().startswith((\"from \", \"import \")):
            idx = i + 1
            break
    lines.insert(idx, needle)
    return \"\\n\".join(lines) + (\"\\n\" if not s.endswith(\"\\n\") else \"\")

src = ensure_line(src, \"from fastapi.middleware.cors import CORSMiddleware\")
src = ensure_line(src, \"from fastapi.staticfiles import StaticFiles\")

p.write_text(src, encoding=\"utf-8\")
print(\"OK: CORSMiddleware/StaticFiles imports ensured.\")
'@ | Set-Content -Encoding UTF8 scripts\fix_cors_import.py"

REM --- venv & deps ---
if not exist .venv (
  echo Creating venv...
  py -3 -m venv .venv
)
echo Upgrading pip...
call .venv\Scripts\python.exe -m pip install --upgrade pip
echo Installing requirements...
call .venv\Scripts\python.exe -m pip install -r requirements.txt

REM --- repair code imports ---
echo Fixing main.py imports...
call .venv\Scripts\python.exe scripts\force_fix_main_header.py
call .venv\Scripts\python.exe scripts\fix_cors_import.py

REM --- init git & first commit ---
if not exist .git (
  git init
  git checkout -b main
)
git add .
git commit -m "chore: bootstrap, git meta, and import fixes" 2>nul

if not "%REMOTE_URL%"=="" (
  git remote remove origin >nul 2>&1
  git remote add origin %REMOTE_URL%
  git push -u origin main
)

echo.
echo ================= NEXT STEPS =================
echo 1) (опционально) Засеять каталог материалов:
echo    .venv\Scripts\python.exe seed_catalog.py
echo 2) Запустить сервер:
echo    .venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
echo 3) Открыть в браузере: http://localhost:8000/
echo =================================================
pause
endlocal
