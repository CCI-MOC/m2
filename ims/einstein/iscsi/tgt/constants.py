CEPH_ID_KEY = 'id'
CEPH_POOL_KEY = 'pool'
CEPH_CONFIG_FILE_KEY = 'conf_file'

TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"

ISCSI_IP_KEY = 'ip'

# Commands
START_COMMAND = "service tgtd start"
STOP_COMMAND = "service tgtd stop"
STATUS_COMMAND = "service tgtd status"
TARGET_CREATION_COMMAND = "tgt-admin --execute"
TARGET_DELETION_COMMAND = "tgt-admin -f --delete {0}"
LIST_TARGETS_COMMAND = "tgt-admin -s"

# Template
TEMPLATE_NAME = "tgt_target.temp"
TARGET_NAME = "${target_name}"
CEPH_USER = '${ceph_user}'
CEPH_CONFIG = '${ceph_config}'
CEPH_POOL = '${pool}'

# Statuses
ACTIVE_STATUS = 'active (running)'
INACTIVE_STATUS = 'inactive (dead)'

ACTIVE_STATE = 0
DEAD_STATE = 1
ERROR_STATE = 2
