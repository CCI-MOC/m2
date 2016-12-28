# Config Keys
ISCSI_PASSWORD_KEY = 'password'
ISCSI_IP_KEY = 'ip'

TGT_ISCSI_CONFIG = "/etc/tgt/conf.d/"
TGT_TEMP_NAME = "tgt_target.temp"
TGT_ADMIN_PATH = "/usr/sbin/tgt-admin"

# Template Parameters
TGT_POOL_NAME = '${pool}'
TGT_TARGET_NAME = '${target_name}'
TGT_CEPH_ID = '${ceph_user}'
TGT_CEPH_CONFIG = '${ceph_config}'