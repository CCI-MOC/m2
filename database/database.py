
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# The class which represents the BMI database
# It is responsible for creating and closing sessions
class Database:

    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()

    # creates the engine for the database, creates all tables if not present and creates a Session Maker
    def __init__(self):
        # test.db should be changed to something more realistic
        self.engine = create_engine('sqlite:///test.db', poolclass = NullPool)
        Database.Base.metadata.create_all(self.engine)
        self.Session_Maker = sessionmaker(bind=self.engine)

    # create a session to the db
    def create_session(self):
        self.session = self.Session_Maker()

    # closes the session to the db
    def close_session(self):
        self.session.close()


