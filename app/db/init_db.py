from sqlalchemy import inspect
from app.db.session import engine
from app.db.base import Base
from app import models  # noqa

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables:", inspect(engine).get_table_names())
