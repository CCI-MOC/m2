from image import *


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
