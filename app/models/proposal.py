from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True)
    number = Column(String(50))
    title = Column(String(200), default="Коммерческое предложение")
    customer_id = Column(Integer, ForeignKey("customers.id"))
    site_address = Column(String(300))
    header_html = Column(String(500), default="")
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    customer = relationship("Customer")

class ProposalSection(Base):
    __tablename__ = "proposal_sections"
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    title = Column(String(200), nullable=False)
    position = Column(String(20))
    proposal = relationship("Proposal", backref="sections")

class ProposalItem(Base):
    __tablename__ = "proposal_items"
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("proposal_sections.id"))
    name = Column(String(300), nullable=False)    # Наименование и тех. характеристика
    note = Column(String(300))                    # Тип, марка, обозначение
    unit = Column(String(50), default="шт")
    qty = Column(Float, default=1.0)
    price = Column(Float, default=0.0)            # материалы/оборудование, за ед.
    price_labor = Column(Float, default=0.0)      # монтаж, за ед.
    position = Column(String(20))
    proposal = relationship("Proposal", backref="items")
    section = relationship("ProposalSection")
