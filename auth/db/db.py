from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid
import sqlite3
from utils.backoff import backoff
from settings import DATABASE_URL

sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
engine = create_engine(DATABASE_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
session = db_session()
Base = declarative_base()
Base.query = db_session.query_property()


@backoff()
def init_db():
    import models.user
    Base.metadata.create_all(bind=engine)
