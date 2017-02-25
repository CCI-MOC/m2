# This is a wrapper for subprocess that must be used by all shell calls
# The sudo in this doesnt take password as we wont be needing it.
# shell=True must never be used

import subprocess


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
    output = subprocess.check_output(s_command, stderr=subprocess.STDOUT)
    return output
