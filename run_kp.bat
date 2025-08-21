@echo off
setlocal enabledelayedexpansion

REM ===== KP Suite ULTRA launcher (robust) =====
cd /d %~dp0

if not exist .venv (
  echo Creating virtual environment...
  py -3 -m venv .venv
)

set "PY=.venv\Scripts\python.exe"

echo Activating venv...
call .venv\Scripts\activate

echo Upgrading pip inside venv...
"%PY%" -m pip install --upgrade pip

echo Installing requirements into venv...
"%PY%" -m pip install -r requirements.txt

echo Starting KP Suite ULTRA...
set ADMIN_USER=admin
set ADMIN_PASS=admin
"%PY%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
