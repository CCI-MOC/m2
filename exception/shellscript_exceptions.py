from bmi_exceptions import ShellScriptException


class NodeAlreadyInUseException(ShellScriptException):
    def __str__(self):
        return "Node Already in Use"


class NodeAlreadyUnmappedException(ShellScriptException):
    def __str__(self):
        return "Node Already Unmapped"
