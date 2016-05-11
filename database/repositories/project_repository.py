from database import *


class ProjectRepository:
    # inserts this object into the table
    # commits after insertion otherwise rollback occurs after which exception is bubbled up

    def __init__(self):
        self.connection = None

    def insert(self, name, provision_network):
        try:
            self.connection = DatabaseConnection()
            p = Project()
            p.name = name
            p.provision_network = provision_network
            self.connection.session.add(p)
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # deletes project with name
    # commits after deletion otherwise rollback occurs after which exception is bubbled up
    def delete_with_name(self, name):
        try:
            self.connection = DatabaseConnection()
            self.connection.session.delete(self.connection.session.query(Project).filter_by(name=name).first())
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # fetch the project with name
    # only project object is returned as the name is unique
    def fetch_id_with_name(self, name):
        try:
            self.connection = DatabaseConnection()
            for project in self.connection.session.query(Project).filter_by(name=name):
                return project.id
        # should change to more specific exception
        except Exception:
            print "Database Exception: Something bad happened related to database"
        finally:
            self.connection.close()
