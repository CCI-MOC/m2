#!/bin/bash
############################
# Usage : iscsi_update.sh <keyring> <id>  <pool> <nodename>#
#                                                          # 
############################
key=$1
id=$2
pool=$3
nodeName=$4
whisper=$6
operation=$5
#rbdev=`echo $whisper |sudo -S rbd --keyring /etc/ceph/client.henn.key \
#    --id henn map $pool/$nodeName`
if [ "$operation" == "create" ] ; then
#Creating an isci target 
    if `echo $whisper | sudo -S grep -q $nodeName /etc/iet/ietd.conf`; then
        echo "This node is already part of iscsi server"
        exit
    else
        rbdev=`echo $whisper |sudo -S rbd --keyring $key  \
        --id $id map $pool/$nodeName`
        echo "Target iqn.2015.$nodeName"|sudo -S tee -a /etc/iet/ietd.conf

        echo "        Lun 0 Path=$rbdev,Type=blockio,ScsiId=lun0,ScsiSN=lun0" \
            |sudo -S tee -a /etc/iet/ietd.conf
    echo "Node added successfully"
# **Script complete** #
    echo $whisper | sudo -S ls > /dev/null
    set -x
    sudo service iscsitarget restart
    fi
elif [ $operation == "delete" ]; then
    echo $whisper | sudo -S ls > /dev/null
    #rbdev=`rbd showmapped|grep $nodeName|awk '{print $5;}'`
    target=`rbd showmapped | grep $nodeName | awk '{print $5;}'`
    #target=`rbd showmapped | awk '{print $3" "$5;}' | grep -w '^$nodename' | awk '{print $2;}''`
    if [ "$target" == '' ]; then
      echo "Node is already unmapped" 
    else
      sudo cp /etc/iet/ietd.conf /etc/iet/ietd.conf_$myDate
      sudo cat /etc/iet/ietd.conf > /tmp/ietd_tmp
      cat /tmp/ietd_tmp |egrep -v $nodeName'|'$target > /tmp/ietd_tmp01
      cp /tmp/ietd_tmp01 /tmp/ietd_tmp
      sudo cp /tmp/ietd_tmp /etc/iet/ietd.conf
      sudo chown root:root /etc/iet/ietd.conf
      sudo chmod 600 /etc/iet/ietd.conf
      sudo service iscsitarget stop
      echo "Successfully removed isci-targets for $nodeName"
      echo "releasing $target"
      sudo rbd unmap $target
      echo "Block device for $target unmapped successfully"
      sudo service iscsitarget start
    fi 
fi
