from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

import ims.common.config as config

_cfg = config.get()

# creates the engine for the database
# Should be adapted to postgres SQL
engine = create_engine('sqlite:///' + _cfg.db.path,
                       poolclass=SingletonThreadPool)


# The class which represents the BMI database
# It is responsible for creating and closing sessions
class DatabaseConnection:
    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()

    # creates all tables if not present
    def __init__(self):
        # creates a session maker for creating sessions
        session_maker = sessionmaker(bind=engine)

        DatabaseConnection.Base.metadata.create_all(engine)
        self.session = session_maker()

    def close(self):
        self.session.close()
