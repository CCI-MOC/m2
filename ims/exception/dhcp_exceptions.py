from ims.exception.exception import DHCPException


class MacAddrNotFoundException(DHCPException):
    @property
    def status_code(self):
        return 404

    def __init__(self, mac_addr):
        self.mac_addr = mac_addr

    def __str__(self):
        return self.mac_addr + " Has Not Been Assigned An IP Yet"
