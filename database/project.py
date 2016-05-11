from database import DatabaseConnection
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


# This class represents the project table
# the Column variables are the columns in the table
# the relationship variable is loaded eagerly as the session is terminated after the object is retrieved
# The relationship is also delete on cascade
# images relationship is a reverse relation for easy traversal if required
class Project(DatabaseConnection.Base):
    __tablename__ = "project"

    # Columns in the table
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    provision_network = Column(String, nullable=False)

    # Relationships in the table, this one back populates to project in Image Class, eagerly loaded
    # and cascade on delete is enabled
    images = relationship("Image", back_populates="project", lazy="joined", cascade="all, delete, delete-orphan")

    def __init__(self):
        self.connection = None

    # inserts this object into the table
    # commits after insertion otherwise rollback occurs after which exception is bubbled up
    def insert(self):
        try:
            self.connection = DatabaseConnection()
            self.connection.session.add(self)
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # deletes project with name
    # commits after deletion otherwise rollback occurs after which exception is bubbled up
    def delete(self):
        try:
            self.connection = DatabaseConnection()
            self.connection.session.delete(self)
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # fetch the project with name
    # only project object is returned as the name is unique
    @staticmethod
    def fetch_with_name(name):
        connection = DatabaseConnection()
        try:
            return connection.session.query(Project).filter_by(name=name).first()
        # should change to more specific exception
        except Exception:
            print "Database Exception: Something bad happened related to database"
        finally:
            connection.close()


