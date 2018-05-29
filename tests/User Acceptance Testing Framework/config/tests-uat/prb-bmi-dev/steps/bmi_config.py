
PROVISIONING_DELAY = 10

LOG_FILE_MINIMUM_THRESHOLD_OF_LINE_NUMBER_WRITES = 10

RBD_CREATE = "rbd_create"
IMAGE_NAME = "image_name"
CEPH_CLONE_NAME = "ceph_clone_name"
PROJECT_NAME = "project_name"
BMI_IMPORT = "bmi_import"
BMI_PROVISION = "bmi_provision"
NODE_NAME = "node_name"
NETWORK_NAME = "network_name"
NIC = "NIC"
BMI_SNAPSHOT = "bmi_snapshot"
SNAPSHOT_NAME = "snapshot_name"

EXPECTED_OUTPUT = {
   'bmi_import_image'   : "Success",
   'bmi_remove_image'   : "Success",
   'bmi_provision_node' : "Success",
   'bmi_deprovision_node' : "Success",
   'bmi_snapshot_node' : "Success",
   'rbd_rm' : "Removing image: 100% complete...done."
}

