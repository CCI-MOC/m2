from database import DatabaseConnection
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


# This class represents the image table
# the Column variables are the columns in the table
# the relationship variables is loaded eagerly as the session is terminated after the object is retrieved
# The snaphosts relationship is also delete on cascade (Commented)
# snapshots relationship is a reverse relation for easy traversal if required (Commented)
class Image(DatabaseConnection.Base):
    __tablename__ = "image"

    # Columns in the table
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    # Relationships in the table
    # Back populates to images in Project Class and is eagerly loaded
    project = relationship("Project", back_populates="images", lazy="joined")

    # Removed snapshot class for now
    # snapshots = relationship("Snapshot", back_populates="image", lazy="joined", cascade="all, delete, delete-orphan")

    def __init__(self):
        self.connection = None

    # inserts the contents of this object into table
    # Commits if inserted successfully otherwise rollbacks if some issue occured and bubbles the exception
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

    # deletes images with name
    # commits if deletion was successful otherwise rollback occurs and exception is bubbled up
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

    # fetch image with name in project with name
    # returns a array of image objects which match the names
    @staticmethod
    def fetch_with_name_from_project(name, project_name):
        connection = DatabaseConnection()
        try:
            images = []
            for image in connection.session.query(Image).filter_by(name=name):
                if image.project.name == project_name:
                    images.append(image)
            return images
        # should change to more specific exception
        except Exception:
            print "Database Exception: Something bad happened related to database"
        finally:
            connection.close()
