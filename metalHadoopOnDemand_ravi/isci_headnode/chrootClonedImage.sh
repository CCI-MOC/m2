#!/bin/bash

source /home/user/metalHadoopOnDemand/mysecret

# ** USAGE MESSAGE ** #
Usage () {
    printf "Usage: $0 [mount_node <node_name>] \
       \n\t\t\t\t [unmount_node <node_name> ]\
       \n\t\t\t\t [restart_ietd ]\
       \n\t\t\t\t [edit_node <node_name> ]\n"
    exit 1; }

[ $# -eq 0 ] && Usage


mount_node() {
    set -x
    echo $whisper | sudo -S ls > /dev/null
    nodeId=`echo $1 | cut -d"-" -f2`
    a=`sudo rbd showmapped | grep $1 | awk '{print $5;}'`
    target_device=${a:5}
    #echo "$target_device"

    
    sudo losetup /dev/loop0 $a
    sudo kpartx -a /dev/loop0
    sudo vgchange -ay centos
    sudo mount /dev/mapper/centos-root /mnt/hadoop
}

unmount_node() {
    echo $whisper | sudo -S ls > /dev/null
    set -x
    a=`sudo rbd showmapped | grep $1 | awk '{print $5;}'`
    target_device=${a:5}
    nodeId=`echo $1 | cut -d"-" -f2`
    
    sudo umount /mnt/hadoop
    sudo sudo vgremove --force centos
    sudo kpartx -d /dev/loop0
    sudo losetup -d /dev/loop0
}

edit_node() {
    echo $whisper | sudo -S ls > /dev/null
    set -x
    nodeId=`echo $1 | cut -d"-" -f2`
    newMaster="bigdata$nodeId.moc.ne.edu"
    oldMaster="bigdata12.moc.ne.edu"
    echo $newMaster
    sudo sed -i -- "s/$oldMaster/$newMaster/g" /mnt/hadoop/opt/hadoop/etc/hadoop/yarn-site.xml
    sudo sed -i -- "s/$oldMaster/$newMaster/g" /mnt/hadoop/opt/hadoop/etc/hadoop/core-site.xml
}


restart_ietd_service() {
    echo $whisper | sudo -S ls > /dev/null
    set -x
    sudo service iscsitarget restart
}


case  "$1"  in

    mount_node)
	mount_node $2
	;;

    unmount_node)
	unmount_node $2
	;;

    edit_node)
	edit_node $2
	;;

    restart_ietd)
	restart_ietd_service
	;;


    *)
	Usage
	;;
    esac
