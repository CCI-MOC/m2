#!/bin/bash

# Argument 1: The golden image name
# Argument 2: The Ceph image name
# Example ./cleanup-first-pass.sh bmi-test-image 5img1

rbd snap unprotect ${2}@snapshot
rbd snap purge $2
rbd rm $2
bmi db rm $1 $2
