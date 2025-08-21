from sqlalchemy import Column, Integer, String
from app.db.base import Base
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer)
    kind = Column(String(50), nullable=False, default="materials")
