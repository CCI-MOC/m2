import ims.common.constants as constants
import ims.exception.dhcp_exceptions as dhcp_exceptions


class DNSMasq:
    def get_ip(self, mac_addr):
        with open(constants.DNSMASQ_LEASES_LOC, 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                if parts[1] == mac_addr and parts[4] == '01:' + mac_addr:
                    return parts[2]
            raise dhcp_exceptions.MacAddrNotFoundException(mac_addr)
