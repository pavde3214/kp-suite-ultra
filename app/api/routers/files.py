from fastapi import APIRouter, Query
from app.services.files import safe_file_response
router = APIRouter(tags=["files"])
@router.get("/files")
def files(path: str = Query(..., description="Имя файла из storage/docs")):
    return safe_file_response(path)
