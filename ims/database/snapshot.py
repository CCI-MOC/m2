from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


# Dont need it for now. Keeping just in case and is incomplete

# This class represents the image table  # the Column variables are the columns
# in the table the relationship variable is loaded eagerly as the session is
# terminated after the object is retrieved
class Snapshot():
    __tablename__ = "snapshot"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    image_id = Column(Integer, ForeignKey("image.id"), nullable=False)

    image = relationship("Image", back_populates="snapshots", lazy="joined")

    def __init__(self, db):
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

    def delete_with_name(self, name):
        try:
            self.database.create_session()
            for image in self.database.session.query(Snapshot).filter_by(
                    name=name):
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
            for image in self.database.session.query(Image).filter_by(
                    name=name):
                if image.project.name == project_name:
                    images.append(image)

            return images

        except Exception as e:
            print "Database Exception: Something bad happened related to " \
                  "database"
        finally:
            self.database.close_session()
