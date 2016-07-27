from ims.exception.dhcp_exceptions import *
import ims.common.constants as constants

class DNSMasq:
    def get_ip(self, mac_addr):
        with open(constants.DNSMASQ_LEASES_LOC, 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                if parts[1] == mac_addr and parts[4] == '01:' + mac_addr:
                    return parts[2]
            raise MacAddrNotFoundException(mac_addr)
