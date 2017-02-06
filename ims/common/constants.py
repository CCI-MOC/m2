# Config Flags
PICASSO_CONFIG_FLAG = 'picasso'
EINSTEIN_CONFIG_FLAG = 'einstein'

# Config Default Locations
CONFIG_DEFAULT_LOCATION = '/etc/bmi/bmiconfig.cfg'

# Environment Variable Names
CONFIG_LOCATION_ENV_VARIABLE = 'BMI_CONFIG'
PROJECT_ENV_VARIABLE = 'PROJECT'
HIL_USERNAME_VARIABLE = 'HIL_USERNAME'
HIL_PASSWORD_VARIABLE = 'HIL_PASSWORD'

# Config section names
BMI_SECTION = 'bmi'
DB_SECTION = 'db'
FS_SECTION = 'fs'
NET_ISOLATOR_SECTION = 'net_isolator'
ISCSI_SECTION = 'iscsi'
RPC_SECTION = 'rpc'
REST_API_SECTION = 'rest_api'
LOGS_SECTION = 'logs'
TFTP_SECTION = 'tftp'
TESTS_SECTION = 'tests'
DRIVER_SECTION = 'driver'

NET_ISOLATOR_DRIVER_OPT = 'net_isolator'
ISCSI_DRIVER_OPT = 'iscsi'
FS_DRIVER_OPT = 'fs'

# Network Isolator Keys
NET_ISOLATOR_URL_OPT = 'url'

# ISCSI Keys
ISCSI_PASSWORD_OPT = 'password'
ISCSI_IP_OPT = 'ip'

# DB
DB_PATH_OPT = 'path'

# Ceph Keys in Config File
CEPH_ID_OPT = 'id'
CEPH_POOL_OPT = 'pool'
CEPH_CONFIG_FILE_OPT = 'conf_file'
CEPH_KEY_RING_OPT = 'keyring'

# ISCSI
ISCSI_UPDATE_SUCCESS = 'successfully'
ISCSI_UPDATE_FAILURE = 'already'
ISCSI_CREATE_COMMAND = 'create'
ISCSI_DELETE_COMMAND = 'delete'

# RPC
NAME_SERVER_IP_OPT = 'name_server_ip'
NAME_SERVER_PORT_OPT = 'name_server_port'
RPC_SERVER_IP_OPT = 'rpc_server_ip'
RPC_SERVER_PORT_OPT = 'rpc_server_port'

RPC_SERVER_NAME = 'example.mainserver'

# REST_API
REST_API_IP_OPT = 'ip'
REST_API_PORT_OPT = 'port'

# LOGS
LOGS_PATH_OPT = 'path'
LOGS_DEBUG_OPT = 'debug'
LOGS_VERBOSE_OPT = 'verbose'

# TFTP
PXELINUX_PATH_OPT = 'pxelinux_path'
IPXE_PATH_OPT = 'ipxe_path'

# BMI
UID_OPT = 'uid'
SERVICE_OPT = 'service'

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

IET_MAPPING_TEMP = 'Target iqn.2015.${ceph_img_name}\n        ' \
                   'Lun 0 Path=${rbd_name},Type=blockio,ScsiId=lun0,ScsiSN=' \
                   'lun0\n'
IET_ISCSI_CONFIG_LOC = '/etc/iet/ietd.conf'
IET_ISCSI_CONFIG_TEMP_LOC = '/etc/iet/ietd.temp'
IET_TARGET_STARTING = 'Target'
IET_LUN_STARTING = "Lun"

DNSMASQ_LEASES_LOC = '/var/lib/misc/dnsmasq.leases'

HIL_CALL_TIMEOUT = 10
DEFAULT_SNAPSHOT_NAME = "snapshot"

BMI_ADMIN_PROJECT = "bmi_infra"

HIL_BMI_CHANNEL = "vlan/native"
