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

    def get_ipxe_path(self, cfg, node_name):
        """
        Given the configuration file and node name, returns the
        path to the ipxe file.

        :param cfg: BMI configuration file
        :param node_name: Name of the node
        :return: Returns the path to the ipxe file for the given node
        """
        return cfg.tftp.ipxe_path + node_name + ".ipxe"
