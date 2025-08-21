from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse
from app.config import DOCS_DIR
SAFE_ROOT = DOCS_DIR.resolve()
def safe_file_response(rel_or_abs_path: str):
    p = Path(rel_or_abs_path)
    p = (SAFE_ROOT / p).resolve() if not p.is_absolute() else p.resolve()
    if SAFE_ROOT not in p.parents and p != SAFE_ROOT:
        raise HTTPException(403, "forbidden")
    if not p.is_file():
        raise HTTPException(404, "file not found")
    return FileResponse(str(p))
