from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base
class TemplateRec(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)  # 'Договор.docx', ...
    path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
