from database import DatabaseConnection
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError


# This class is responsible for doing CRUD operations on the Project Table in DB
# This class was written as per the Repository Model which allows us to change the DB in the future without changing
# business code
class ProjectRepository:
    def __init__(self):
        self.connection = None

    # inserts the arguments into the table
    # commits after insertion otherwise rollback occurs after which exception is bubbled up
    def insert(self, name, provision_network):
        try:
            self.connection = DatabaseConnection()
            p = Project()
            p.name = name
            p.provision_network = provision_network
            self.connection.session.add(p)
            self.connection.session.commit()
        except SQLAlchemyError:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # deletes project with name
    # commits after deletion otherwise rollback occurs after which exception is bubbled up
    def delete_with_name(self, name):
        try:
            self.connection = DatabaseConnection()
            self.connection.session.query(Project).filter_by(name=name).delete(synchronize_session=False)
            self.connection.session.commit()
        except SQLAlchemyError:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # fetch the project id with name
    # only project object is returned as the name is unique
    def fetch_id_with_name(self, name):
        try:
            self.connection = DatabaseConnection()
            # could use first() but method doesnt return None when project with name doesnt exist and may crash in that
            # case
            for project in self.connection.session.query(Project).filter_by(name=name):
                return project.id
        except SQLAlchemyError:
            print "Database Exception: Something bad happened related to database"
        finally:
            self.connection.close()


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
    images = relationship("Image", back_populates="project", cascade="all, delete, delete-orphan")
