# This is a wrapper for subprocess that must be used by all shell calls
# The sudo in this doesnt take password as we wont be needing it.
# shell=True must never be used

import subprocess


# Calls Command
def call(command, sudo=False):
    s_command = command.split()
    if sudo:
        s_command.insert(0, 'sudo')
    output = subprocess.check_output(s_command, stderr=subprocess.STDOUT)
    return output
