from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship

import ims.exception.db_exceptions as db_exceptions
from ims.common.log import create_logger, log, trace
from ims.database.db_connection import DatabaseConnection

logger = create_logger(__name__)


# This class is responsible for doing CRUD operations on the Project Table in
# DB. This class was written as per the Repository Model which allows us to
# change the DB in the future without changing business code
class ProjectRepository:
    @trace
    def __init__(self, connection):
        self.connection = connection

    # inserts the arguments into the table
    # commits after insertion otherwise rollback occurs after which exception
    # is bubbled up
    @log
    def insert(self, name, provision_network, id=None):
        try:
            p = Project()
            p.name = name
            p.provision_network = provision_network
            if id is not None:
                p.id = id
            self.connection.session.add(p)
            self.connection.session.commit()
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)

    # deletes project with name
    # commits after deletion otherwise rollback occurs after which exception is
    # bubbled up
    @log
    def delete_with_name(self, name):
        try:
            project = self.connection.session.query(Project).filter_by(
                name=name).one_or_none()
            if project is not None:
                self.connection.session.delete(project)
                self.connection.session.commit()
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)

    # fetch the project id with name
    # only project object is returned as the name is unique
    @log
    def fetch_id_with_name(self, name):
        try:
            project = self.connection.session.query(Project).filter_by(
                name=name).one_or_none()
            if project is not None:
                return project.id
        except SQLAlchemyError as e:
            raise db_exceptions.ORMException(e.message)

    @log
    def fetch_projects(self):
        try:
            projects = self.connection.session.query(Project)
            return [[project.id, project.name, project.provision_network] for
                    project in projects]
        except SQLAlchemyError as e:
            raise db_exceptions.ORMException(e.message)


# This class represents the project table
# the Column variables are the columns in the table
# the relationship variable is loaded eagerly as the session is terminated
# after the object is retrieved. The relationship is also delete on cascade
# images relationship is a reverse relation for easy traversal if required
class Project(DatabaseConnection.Base):
    __tablename__ = "project"

    # Columns in the table
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    provision_network = Column(String, nullable=False)

    # Relationships in the table, this one back populates to project in Image
    # Class, eagerly loaded and cascade on delete is enabled
    images = relationship("Image", back_populates="project",
                          cascade="all, delete, delete-orphan")
