from database.tables.project import *
from exception import db_exceptions
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
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)
        finally:
            self.connection.close()

    # deletes project with name
    # commits after deletion otherwise rollback occurs after which exception is bubbled up
    def delete_with_name(self, name):
        try:
            self.connection = DatabaseConnection()
            self.connection.session.delete(self.connection.session.query(Project).filter_by(name=name).first())
            self.connection.session.commit()
        except SQLAlchemyError as e:
            self.connection.session.rollback()
            raise db_exceptions.ORMException(e.message)
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
        except SQLAlchemyError as e:
            raise db_exceptions.ORMException(e.message)
        finally:
            self.connection.close()
