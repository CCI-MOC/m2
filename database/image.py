from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Database


# This class represents the image table  # the Column variables are the columns in the table
# the relationship variables is loaded eagerly as the session is terminated after the object is retrieved
# The snaphosts relationship is also delete on cascade
# snapshots relationship is a reverse relation for easy traversal if required
class Image(Database.Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)

    project = relationship("Project", back_populates="images", lazy="joined")

    # Removed snapshot class for now
    # snapshots = relationship("Snapshot", back_populates="image", lazy="joined", cascade="all, delete, delete-orphan")


    def __init__(self,db):
        self.database = db



    def insert(self):
        try:
            self.database.create_session()
            self.database.session.add(self)
            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            raise

        finally:
            self.database.close_session()

    def delete_with_name(self,name):
        try:
            self.database.create_session()
            for image in self.database.session.query(Image).filter_by(name = name):
                self.database.delete(image)

            self.database.session.commit()
        except Exception as e:
            self.database.session.rollback()
            raise
        finally:
            self.database.close_session()


    def fetch_with_name_from_project(self, name, project_name):
        try:
            self.database.create_session()
            images = []
            for image in self.database.session.query(Image).filter_by(name = name):
                if image.project.name == project_name:
                    images.append(image)

            return images

        except Exception as e:
            print "Database Exception: Something bad happened related to database"
        finally:
            self.database.close_session()