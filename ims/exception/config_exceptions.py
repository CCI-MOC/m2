from ims.exception.exception import ConfigException


class MissingOptionInConfigException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, option):
        self.option = option

    def __str__(self):
        return "Missing " + self.option + " option in bmi config file"


class DriverKeyNotFoundException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, section_name):
        self.section = section_name

    def __str__(self):
        return "Missing Driver Key in " + self.section + " section"
