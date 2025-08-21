from sqlalchemy import Column, Integer, String
from app.db.base import Base
class Owner(Base):
    __tablename__ = "owner"
    id = Column(Integer, primary_key=True)
    display_name = Column(String(200), default="Исполнитель")
    fullname = Column(String(200))
    passport = Column(String(200))
    address = Column(String(300))
    phone = Column(String(100))
    email = Column(String(150))
    inn = Column(String(50))
    ogrn = Column(String(50))
