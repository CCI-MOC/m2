CEPH_ID_KEY = 'id'
CEPH_POOL_KEY = 'pool'
CEPH_KEY_RING_KEY = 'keyring'

ISCSI_IP_KEY = 'ip'

# Commands
MAP_COMMAND = "rbd --keyring {1} --id {2} map {3}/{4}"
UNMAP_COMMAND = "rbd --keyring {1} --id {2} unmap {3}"
LIST_MAPPED_COMMAND = "rbd showmapped"
RESTART_COMMAND = "service iscsitarget restart"
STATUS_COMMAND = "service iscsitarget status"
STOP_COMMAND = "service iscsitarget stop"
START_COMMAND = "service iscsitarget start"

IET_MAPPING_TEMP = 'Target ${ceph_img_name}\n        ' \
                   'Lun 1 Path=${rbd_name},Type=blockio,ScsiId=lun1,ScsiSN=' \
                   'lun1\n'
IET_ISCSI_CONFIG_LOC = '/etc/iet/ietd.conf'
IET_ISCSI_CONFIG_TEMP_LOC = '/etc/iet/ietd.temp'
IET_TARGET_STARTING = 'Target'
IET_LUN_STARTING = "Lun"

CEPH_IMG_NAME = "${ceph_img_name}"
RBD_NAME = "${rbd_name}"

# Statuses
ACTIVE_STATUS = 'active (running)'
INACTIVE_STATUS = 'inactive (dead)'

ACTIVE_STATE = 0
DEAD_STATE = 1
ERROR_STATE = 2
