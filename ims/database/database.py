from ims.common.log import log
from ims.database.db_connection import DatabaseConnection
from ims.database.image import ImageRepository
from ims.database.project import ProjectRepository


class Database:
    @log
    def __init__(self):
        self.__connection = DatabaseConnection()
        self.project = ProjectRepository(self.__connection)
        self.image = ImageRepository(self.__connection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @log
    def close(self):
        self.__connection.close()
