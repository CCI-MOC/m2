#!/bin/bash

# Argument 1: The golden or Ceph image name
# Example ./cleanup-rbd.sh bmi-test-image

rbd snap unprotect ${1}@snapshot
rbd snap purge $1
rbd rm $1


