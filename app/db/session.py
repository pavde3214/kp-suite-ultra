from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import DB_URL

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}
engine = create_engine(DB_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
