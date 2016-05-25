from exception import ShellScriptException


# this exception should be raised when the shell script is called on a node that is already in use
class NodeAlreadyInUseException(ShellScriptException):
    def __str__(self):
        return "Node Already in Use"


# this exception should be raised when the shell script is called on a node that is already unmapped
class NodeAlreadyUnmappedException(ShellScriptException):
    def __str__(self):
        return "Node Already Unmapped"
