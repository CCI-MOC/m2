
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Database

# This class represents the project table
# the Column variables are the columns in the table
# the relationship variable is loaded eagerly as the session is terminated after the object is retrieved
# The relationship is also delete on cascade
# images relationship is a reverse relation for easy traversal if required


class Project(Database.Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    provision_network = Column(String, nullable=False)

    images = relationship("Image", back_populates="project", lazy="joined", cascade="all, delete, delete-orphan")

    def __init__(self,db):
        self.database = db

    def insert(self):
        try:
            self.database.create_session()
            self.database.session.add(self)
            self.database.session.commit()
        # should change to more specific exception
        except Exception as e:
            self.database.session.rollback()
            raise

        finally:
            self.database.close_session()


    def delete_with_name(self,name):
        try:
            self.database.create_session()
            for project in self.database.session.query(Project).filter_by(name = name):
                self.database.delete(project)

            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            raise
        finally:
            self.database.close_session()


    def fetch_with_name(self,name):
        try:
            self.database.create_session()
            for project in self.database.session.query(Project).filter_by(name = name):
                return project
        except Exception as e:
            print "Database Exception: Something bad happened related to database"
        finally:
            self.database.close_session()