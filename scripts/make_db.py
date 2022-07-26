from sqlalchemy import create_engine

from database.models import Base
from config import SQL_PATH

engine = create_engine(SQL_PATH)
Base.metadata.create_all(engine)
