from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Estimate(Base):
    __tablename__ = "estimates"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), default="Смета")
    customer_id = Column(Integer, ForeignKey("customers.id"))
    site_address = Column(String(300))
    customer = relationship("Customer")

class EstimateSection(Base):
    __tablename__ = "estimate_sections"
    id = Column(Integer, primary_key=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    title = Column(String(200), nullable=False)
    position = Column(String(20))
    estimate = relationship("Estimate", backref="sections")

class EstimateItem(Base):
    __tablename__ = "estimate_items"
    id = Column(Integer, primary_key=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("estimate_sections.id"))
    name = Column(String(300), nullable=False)
    item_type = Column(String(50), default="material")
    unit = Column(String(50), default="шт")
    qty = Column(Float, default=1.0)
    price_material = Column(Float, default=0.0)
    price_labor = Column(Float, default=0.0)
    position = Column(String(20))
    estimate = relationship("Estimate", backref="items")
    section = relationship("EstimateSection")
