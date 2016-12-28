# Config Flags
PICASSO_CONFIG_FLAG = 'picasso'
EINSTEIN_CONFIG_FLAG = 'einstein'

# Config Default Locations
CONFIG_DEFAULT_LOCATION = '/etc/bmi/bmiconfig.cfg'

# Environment Variable Names
CONFIG_LOCATION_ENV_VARIABLE = 'BMI_CONFIG'
PROJECT_ENV_VARIABLE = 'PROJECT'
HIL_USERNAME_VARIABLE = 'HAAS_USERNAME'
HIL_PASSWORD_VARIABLE = 'HAAS_PASSWORD'

# Config prefix section names
FS_PREFIX_CONFIG_NAME = "fs"
ISCSI_PREFIX_CONFIG_NAME = "iscsi"
NETISO_PREFIX_CONFIG_NAME = "netiso"


# Config section names
BMI_CONFIG_SECTION_NAME = 'bmi'
DB_CONFIG_SECTION_NAME = 'db'
RPC_CONFIG_SECTION_NAME = 'rpc'
HTTP_CONFIG_SECTION_NAME = 'http'
LOGS_CONFIG_SECTION_NAME = 'logs'
TFTP_CONFIG_SECTION_NAME = 'tftp'
TESTS_CONFIG_SECTION_NAME = 'tests'

# Non FS Keys in Config File
HIL_URL_KEY = 'url'


# DB
DB_URL_KEY = 'url'

# Ceph Keys in Config File
CEPH_ID_KEY = 'id'
CEPH_POOL_KEY = 'pool'
CEPH_CONFIG_FILE_KEY = 'conf_file'
CEPH_KEY_RING_KEY = 'keyring'


# RPC
RPC_NAME_SERVER_IP_KEY = 'name_server_ip'
RPC_NAME_SERVER_PORT_KEY = 'name_server_port'
RPC_RPC_SERVER_IP_KEY = 'rpc_server_ip'
RPC_RPC_SERVER_PORT_KEY = 'rpc_server_port'

RPC_SERVER_NAME = 'example.mainserver'

# HTTP
BIND_IP_KEY = 'bind_ip'
BIND_PORT_KEY = 'bind_port'

# LOGS
LOGS_URL_KEY = 'url'
LOGS_DEBUG_KEY = 'debug'
LOGS_VERBOSE_KEY = 'verbose'

# TFTP
PXELINUX_URL_KEY = 'pxelinux_url'
IPXE_URL_KEY = 'ipxe_url'

# BMI
UID_KEY = 'uid'
SERVICE_KEY = 'service'

# Response Related Keys
STATUS_CODE_KEY = 'status_code'
RETURN_VALUE_KEY = 'retval'
MESSAGE_KEY = 'msg'

# Commands
LIST_IMAGES_COMMAND = "list_images"
CREATE_SNAPSHOT_COMMAND = "create_snapshot"
PROVISION_COMMAND = "provision"
DEPROVISION_COMMAND = "deprovision"
LIST_SNAPSHOTS_COMMAND = "list_snapshots"
REMOVE_IMAGE_COMMAND = "remove_image"

# Parameters
NODE_NAME_PARAMETER = 'node'
IMAGE_NAME_PARAMETER = "img"
SNAP_NAME_PARAMETER = "snap_name"
PROJECT_PARAMETER = "project"
SRC_PROJECT_PARAMETER = 'src_project'
DEST_PROJECT_PARAMETER = "dest_project"
IMAGE1_NAME_PARAMETER = "img1"
IMAGE2_NAME_PARAMETER = "img2"
NETWORK_PARAMETER = "network"
NIC_PARAMETER = "nic"
CHANNEL_PARAMETER = "channel"

# Template Parameters
IPXE_TARGET_NAME = "${target_name}"
IPXE_ISCSI_IP = "${iscsi_ip}"
MAC_IMG_NAME = "${img_name}"
MAC_IPXE_NAME = "${ipxe.file}"
CEPH_IMG_NAME = "${ceph_img_name}"
RBD_NAME = "${rbd_name}"

IET_MAPPING_TEMP = 'Target ${ceph_img_name}\n        ' \
                   'Lun 1 Path=${rbd_name},Type=blockio,ScsiId=lun1,ScsiSN=lun1\n'
IET_ISCSI_CONFIG_LOC = '/etc/iet/ietd.conf'
IET_ISCSI_CONFIG_TEMP_LOC = '/etc/iet/ietd.temp'
IET_TARGET_STARTING = 'Target'
IET_LUN_STARTING = "Lun"

DNSMASQ_LEASES_LOC = '/var/lib/misc/dnsmasq.leases'

HIL_CALL_TIMEOUT = 10
DEFAULT_SNAPSHOT_NAME = "snapshot"

BMI_ADMIN_PROJECT = "bmi_infra"

HIL_BMI_CHANNEL = "vlan/native"