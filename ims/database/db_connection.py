from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool

import ims.common.config as config
import ims.common.constants as constants

_cfg = config.get()


# The class which represents the BMI database
# It is responsible for creating and closing sessions
class DatabaseConnection:
    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()

    # the engine and session maker are made static so that only one of them
    # needs to be created
    # creates the engine for the database
    # sample_bmi.db should be changed to something more realistic
    # NullPool pool class is equivalent to no connection pool
    # Should be adapted to postgres SQL
    engine = create_engine('sqlite:///' + _cfg.db.path,
                           poolclass=SingletonThreadPool)

    # creates a session maker for creating sessions
    session_maker = sessionmaker(bind=engine)

    # creates all tables if not present
    def __init__(self):
        DatabaseConnection.Base.metadata.create_all(DatabaseConnection.engine)
        self.session = DatabaseConnection.session_maker()

    def close(self):
        self.session.close()
