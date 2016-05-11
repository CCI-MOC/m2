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