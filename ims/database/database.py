from image import *


class Database:
    @log
    def __init__(self):
        self.__connection = DatabaseConnection()
        self.project = ProjectRepository(self.__connection)
        self.image = ImageRepository(self.__connection)

    @log
    def close(self):
        self.__connection.close()
