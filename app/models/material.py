from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.base import Base
class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    model = Column(String(200))
    unit = Column(String(50), default="шт")
    price_material = Column(Float, default=0.0)
    price_labor = Column(Float, default=0.0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
