from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


# The class which represents the BMI database
# It is responsible for creating and closing sessions
class DatabaseConnection:
    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()
    engine = create_engine('sqlite:///sample_bmi.db', poolclass=NullPool)
    session_maker = sessionmaker(bind=engine)
    # creates the engine for the database, creates all tables if not present and creates a Session Maker
    def __init__(self):
        # test.db should be changed to something more realistic
        # NullPool pool class is equivalent to no connection pool
        self.session = DatabaseConnection.session_maker()
        DatabaseConnection.Base.metadata.create_all(DatabaseConnection.engine)

    # closes the session to the db
    def close(self):
        self.session.close()