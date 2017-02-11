import ims.exception.iscsi_exceptions as iscsi_exceptions
from ims.interfaces.iscsi import ISCSI


class MockISCSI(ISCSI):
    """
    This is mock class that implements most of the abstract methods for ISCSI
    class. It returns mostly true or success or some exception. This spoofs the
    requests coming in. This should not have any dependency on file system or
    database or any other component as we are writing unit tests for iSCSI
    server alone. For example, there may be an iSCSI server that implements
    adding target by writing to database instead of files. So, the idea here
    is to touch only services that are core to iSCSI. Other exceptions like
    touching files(for updating configurations) etc, should be handled in
    integration tests or unit tests for that particular iSCSI server. This
    will have helper methods for setting target_lists and server status.
    """
    def __init__(self):
        # Initial target list
        self.target_list = []
        # Initial state of iSCSI server
        self.server_status = ""

    def set_target_list(self, target_list):
        """
        Setter method for target list to be used by test cases.

        Args:
            target_list: List provided by user
        Returns:
            None, will update the list provided.
        """
        self.target_list = target_list

    def set_server_status(self, status):
        """
        Setter method for iSCSI server to be used by test cases.

        Args:
            status: String which has to be either Running or Dead
        Returns:
            Either error state or updates the status of mock iSCSI server
        """
        # TODO: make states constants across all iSCSI implementations.
        VALID_STATES = ["Running", "Dead"]
        error = "iSCSI server in unknown state"
        if status in VALID_STATES:
            self.server_status = status
        else:
            return error

    def add_target(self, target_name):
        """
        Adding a target for iSCSI server.

        Args:
            Adds the target to existing target list
        Returns:
            Returns None if successful or exception. Query list_targets
        to get updated list
        """
        if target_name not in self.list_targets():
            self.target_list.append(target_name)
        else:
            raise iscsi_exceptions.NodeAlreadyInUseException()

    def remove_target(self, target_name):
        """
        Removes a target from iSCSI server.

        Args:
            Name of target that has to be removed.
        Returns:
            None if successful or exception.
        """
        if target_name in self.list_targets():
            self.target_list.remove(target_name)
        else:
            raise iscsi_exceptions.NodeAlreadyUnmappedException()

    def list_targets(self):
        """
        Lists all the targets in current iSCSI server.

        Returns:
            List of all targets.
        """
        return self.target_list

    def start_server(self):
        """
        Starts the iSCSI server.

        Returns:
            None, if successful or an exception.

        """
        # TODO: See my previous comment, modify strings to constants.
        self.server_status = "Running"
        if self.show_status() is not "Running":
            # TODO: I think its better to have a generic StateChangeException.
            raise iscsi_exceptions.StopFailedException()

    def show_status(self):
        """
        Shows the status of iSCSI server.

        Returns:
            String which is either "Running" or "Dead"
        """
        return self.server_status

    def stop_server(self):
        """
        Stops the iSCSI server.

        Returns:
            None if successful or an exception
        """
        # TODO: Same as for start function regarding strings.
        self.server_status = "Dead"
        if self.show_status() is not "Dead":
            raise iscsi_exceptions.StopFailedException()

    def restart_server(self):
        """
        Restarts the iSCSI server.

        Returns:
            None or exception
        """
        self.stop_server()
        self.start_server()
