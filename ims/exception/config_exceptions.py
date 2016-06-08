from exception import ConfigException


class MissingOptionInConfigException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, option):
        self.option = option

    def __str__(self):
        return "Missing " + self.option + " option in bmi config file"
