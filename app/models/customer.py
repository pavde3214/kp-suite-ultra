from sqlalchemy import Column, Integer, String
from app.db.base import Base
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    fullname = Column(String(200), nullable=False)
    passport = Column(String(200))
    address = Column(String(300))
    address_object = Column(String(300))
    phone = Column(String(100))
    email = Column(String(150))
    # реквизиты
    company_name = Column(String(200))
    inn = Column(String(50))
    kpp = Column(String(50))
    ogrn = Column(String(50))
    bank_name = Column(String(200))
    bank_bik = Column(String(50))
    bank_acc = Column(String(50))
    bank_corr = Column(String(50))
    position = Column(String(100))
    contact_person = Column(String(150))
