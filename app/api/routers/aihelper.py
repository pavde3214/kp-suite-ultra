from fastapi import APIRouter
from app.services.ai import suggest_sections_from_text
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])
@router.get("/suggest-sections")
def suggest_sections(text: str):
    return {"sections": suggest_sections_from_text(text)}
