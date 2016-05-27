from exception import ConfigException


class MissingOptionInConfigException(ConfigException):
    def __init__(self, option):
        self.option = option

    def __str__(self):
        return "Missing " + self.option + " option in bmi config file"
