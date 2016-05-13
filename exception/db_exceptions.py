from bmi_exceptions import DBException

class ProjectNotFoundException(DBException):

    def __str__(self):
        return "project not found"

class ImageNotFoundException(DBException):

    def __str__(self):
        return "image not found"

