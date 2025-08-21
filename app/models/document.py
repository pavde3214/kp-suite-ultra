from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base
class DocumentRec(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    estimate_id = Column(Integer)
    kind = Column(String(50))  # contract, kp, appendix1..7, spec, etc.
    title = Column(String(200))
    number = Column(String(100))
    filepath = Column(String(500), nullable=False)
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, server_default=func.now())
