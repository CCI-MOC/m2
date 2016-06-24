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
LOGS_CONFIG_SECTION_NAME = 'logs'

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

# LOGS
LOGS_URL_KEY = 'url'
LOGS_DEBUG_KEY = 'debug'
LOGS_VERBOSE_KEY = 'verbose'

# Response Related Keys
STATUS_CODE_KEY = 'status_code'
RETURN_VALUE_KEY = 'retval'
MESSAGE_KEY = 'msg'

# Commands
LIST_ALL_IMAGES_COMMAND = "list_all_images"
CREATE_SNAPSHOT_COMMAND = "create_snapshot"
PROVISION_COMMAND = "provision"
DETACH_NODE_COMMAND = "detach_node"
LIST_SNAPSHOTS_COMMAND = "list_snaps"
REMOVE_SNAPSHOTS_COMMAND = "remove_snaps"

# Parameters
NODE_NAME_PARAMETER = 'node'
IMAGE_NAME_PARAMETER = "img"
SNAP_NAME_PARAMETER = "snap_name"
PROJECT_PARAMETER = "project"
NETWORK_PARAMETER = "network"
NIC_PARAMETER = "nic"
CHANNEL_PARAMETER = "channel"
