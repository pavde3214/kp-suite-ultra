from sqlalchemy import Column, Integer, String, DateTime, func, Text
from app.db.base import Base
class ContractData(Base):
    __tablename__ = "contract_data"
    id = Column(Integer, primary_key=True)
    number = Column(String(50))
    customer_id = Column(Integer)
    estimate_id = Column(Integer)
    kp_id = Column(Integer)
    ctx_json = Column(Text)  # сохраненные поля договора
    created_at = Column(DateTime, server_default=func.now())
