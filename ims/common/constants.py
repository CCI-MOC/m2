# Config Flags
PICASSO_CONFIG_FLAG = 'picasso'
EINSTEIN_CONFIG_FLAG = 'einstein'

# Config Default Locations
CONFIG_DEFAULT_LOCATION = 'bmiconfig.cfg'

# Environment Variable Names
CONFIG_LOCATION_ENV_VARIABLE = 'BMI_CONFIG'

# Config section names
FILESYSTEM_CONFIG_SECTION_NAME = 'filesystem'
HAAS_CONFIG_SECTION_NAME = 'haas'
CEPH_CONFIG_SECTION_NAME = 'ceph'
ISCSI_CONFIG_SECTION_NAME = 'iscsi'
RPC_CONFIG_SECTION_NAME = 'rpc'
HTTP_CONFIG_SECTION_NAME = 'http'
TFTP_CONFIG_SECTION_NAME = 'tftp'

# Non FS Keys in Config File
HAAS_URL_KEY = 'url'
ISCSI_URL_KEY = 'update_shell_url'
ISCSI_PASSWORD_KEY = 'password'

# Ceph Keys in Config File
CEPH_ID_KEY = 'id'
CEPH_POOL_KEY = 'pool'
CEPH_CONFIG_FILE_KEY = 'conf_file'
CEPH_KEY_RING_KEY = 'keyring'

# ISCSI
ISCSI_UPDATE_SUCCESS = 'successfully'
ISCSI_UPDATE_FAILURE = 'already'
ISCSI_CREATE_COMMAND = 'create'
ISCSI_DELETE_COMMAND = 'delete'

# RPC
RPC_NAME_SERVER_IP_KEY = 'name_server_ip'
RPC_NAME_SERVER_PORT_KEY = 'name_server_port'
RPC_RPC_SERVER_IP_KEY = 'rpc_server_ip'
RPC_RPC_SERVER_PORT_KEY = 'rpc_server_port'

RPC_SERVER_NAME = 'example.mainserver'

# HTTP
BIND_IP_KEY = 'bind_ip'
BIND_PORT_KEY = 'bind_port'

#TFTP
PXELINUX_URL_KEY = 'pxelinux_url'
IPXE_URL_KEY = 'ipxe_url'

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
NETWORK_PARAMETER = "network"
NIC_PARAMETER = "nic"
CHANNEL_PARAMETER = "channel"

# Template Parameters
IPXE_TARGET_NAME = "${target_name}"
MAC_IMG_NAME = "${img_name}"
MAC_IPXE_NAME = "${ipxe.file}"

DEFAULT_SNAPSHOT_NAME = "snapshot"