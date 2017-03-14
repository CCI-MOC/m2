# This is a wrapper for subprocess that must be used by all shell calls
# The sudo in this doesnt take password as we wont be needing it.
# shell=True must never be used
# TODO Add unittests
import subprocess

from ims.common.log import create_logger, trace
from ims.exception import shell_exceptions

logger = create_logger(__name__)


@trace
def call(command, sudo=False):
    """
    Executes the given command in shell

    :param command: the command to execute as string
    :param sudo: whether to execute as root (default is False)
    :return: output of command as string
    """
    s_command = command.split()
    if sudo:
        s_command.insert(0, 'sudo')
    try:
        output = subprocess.check_output(s_command, stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        raise shell_exceptions.CommandFailedException(str(e))


@trace
def call_service_command(command, service_name, final_status=None):
    """
    Calls the given service command and checks whether it has status afterwards

    :param command: service command to call
    :param service_name: The service name
    :param final_status: The final status of the daemon after call
    :return: Output of Call
    """
    full_command = "service %s %s" % (service_name, command)
    output = call(full_command, sudo=True)
    if final_status is not None:
        status = get_service_status(service_name)
        if status is not final_status:
            raise shell_exceptions.ServiceCommandFailedException(status)
    return output


@trace
def get_service_status(service_name):
    """
    Returns the status of given service

    :param service_name: the service whose status should be returned
    :return: Running or Dead or Status String if Error
    """
    status_string = call_service_command('status', service_name)

    if 'active (running)' in status_string:
        return 'Running'
    elif 'inactive (dead)' in status_string:
        return 'Dead'
    # Have to check if there are any other states
    else:
        return status_string
