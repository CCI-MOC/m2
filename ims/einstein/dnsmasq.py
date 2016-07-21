from ims.exception.dhcp_exceptions import *


class DNSMasq:
    def get_ip(self, mac_addr):
        with open('/var/lib/misc/dnsmasq.leases', 'r') as file:
            for line in file:
                parts = line.strip().split(' ')
                if parts[1] == mac_addr and parts[4] == '01:' + mac_addr:
                    return parts[2]
            raise MacAddrNotFoundException(mac_addr)
