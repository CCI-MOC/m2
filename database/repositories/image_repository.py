from database import *


class ImageRepository():
    def __init__(self):
        self.connection = None

    # inserts the contents of this object into table
    # Commits if inserted successfully otherwise rollbacks if some issue occured and bubbles the exception
    def insert(self, image_name, project_id):
        try:
            self.connection = DatabaseConnection()
            img = Image()
            img.name = image_name
            img.project_id = project_id
            self.connection.session.add(img)
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # deletes images with name
    # commits if deletion was successful otherwise rollback occurs and exception is bubbled up
    def delete_with_name_from_project(self, name, project_name):
        try:
            self.connection = DatabaseConnection()
            for img in self.connection.session.query(Image).filter_by(name=name):
                if img.project.name == project_name:
                    self.connection.session.delete(img)
            self.connection.session.commit()
        # should change to more specific exception
        except Exception:
            self.connection.session.rollback()
            raise
        finally:
            self.connection.close()

    # fetch image with name in project with name
    # returns a array of image objects which match the names
    def fetch_ids_with_name_from_project(self, name, project_name):
        try:
            self.connection = DatabaseConnection()
            images = []
            for image in self.connection.session.query(Image).filter_by(name=name):
                if image.project.name == project_name:
                    images.append(image.id)
            return images
        # should change to more specific exception
        except Exception:
            print "Database Exception: Something bad happened related to database"
        finally:
            self.connection.close()
