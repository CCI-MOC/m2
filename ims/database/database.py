from image import *


class Database:
    def __init__(self):
        self.__connection = DatabaseConnection()
        self.project = ProjectRepository(self.__connection)
        self.image = ImageRepository(self.__connection)

    def close(self):
        self.__connection.close()
