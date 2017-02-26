from ims.exception.exception import ConfigException


class MissingOptionInConfigException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, option, section):
        self.option = option
        self.section = section

    def __str__(self):
        return "Missing {0} option in section {1} in config file".format(
            self.option, self.section)


class MissingSectionInConfigException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, section):
        self.option = section

    def __str__(self):
        return "Missing " + self.option + " section in config file"


class InvalidValueConfigException(ConfigException):
    @property
    def status_code(self):
        return 500

    def __init__(self, option, section):
        self.option = option
        self.section = section

    def __str__(self):
        return "Invalid Value for {0} option in section {1}".format(
            self.option, self.section)
