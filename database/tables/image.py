from database import DatabaseConnection
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy import UniqueConstraint
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

    # Users should not be able to create images with same name in a given
    # project. So we are creating a unique constraint.
    UniqueConstraint("project_id", "name", "Project_id_image_name_unique_constraint")

    # Removed snapshot class for now
    # snapshots = relationship("Snapshot", back_populates="image", lazy="joined", cascade="all, delete, delete-orphan")
