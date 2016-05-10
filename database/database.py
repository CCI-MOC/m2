
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# The class which represents the BMI database
# To insert object
# create object of respective table
# populate the object with data
# call insert_object on Database object
# querying and deletion are self explanatory
class Database:

    # the sqlalchemy base class which the table classes will inherit
    Base = declarative_base()

    # creates the engine for the database, creates all tables if not present and creates a Session Maker
    def __init__(self):

        self.engine = create_engine('sqlite:///test.db', poolclass = NullPool)
        Database.Base.metadata.create_all(self.engine)
        self.Session_Maker = sessionmaker(bind=self.engine)

    def create_session(self):
        self.session = self.Session_Maker()
        return self.session

    def close_session(self):
        self.session.close()


