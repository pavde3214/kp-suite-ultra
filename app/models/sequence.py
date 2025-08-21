from sqlalchemy import Column, Integer, String
from app.db.base import Base
class Sequence(Base):
    __tablename__ = "sequences"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    last = Column(Integer, default=0, nullable=False)
