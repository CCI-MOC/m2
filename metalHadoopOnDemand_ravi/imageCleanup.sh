#!/bin/bash
# Title		: imageCleanup.sh
# Description	: Cleans the iscitarget file, unmaps the block device
#			and destroys the associated clone image
# Created	:  2015/11/14
# Usage		: ./imageCleanup.sh help
# Testing	: Create some test images using command
#		  ./clone2isciTarget.sh bigdata slave cisco-100 
#		  Repeat if you want more images eg cisco-101, cisco-102.. etc
# Examples	: imageCleanup.sh rm_target <one or more nodenames >
#		  -- This will remove the entries from the iscsi target file
#		  NOTICE: This should be run as the first call for any node
#		: imageCleanup.sh release cisco-101 
#		  -- This will release the block device associated with cisco-101
#		: imageCleanup.sh destroy cisco-101
#		  -- This will delete the clone associated with cisco-101
#		  WARNING: for any node This should be run 
#		  after "imageCleanup.sh release" is run for that node
#		: imageCleanup.sh remove <one or more nodenames >
#		  -- A single call to accomplish all of the above
# Team		: Sahil, Ata, Jason, Ugur, Ravi 
#
####################################################################################

source mysecret #password for sudo should be stored in a this file. 

nodes=( "$@" )
unset nodes[0]


Usage() {
printf "Usage: $0 [release <node_name>] \
		  \n\t\t\t [destroy <node_name> ] \
		  \n\t\t\t [rm_target <node_name> <name_name> ... ]\
	  	  \n\t\t\t [remove <node_name> <node_name> <node_name> ... ]\
		  \n\t\t\t [help]
"
}


release_rbd() {

    echo $whisper | sudo -S ls > /dev/null
    target=`rbd showmapped | grep $1 | awk '{print $5;}'`
    echo "releasing $target"
    sudo rbd unmap $target
    echo "Block device for $1 unmapped successfully"
}

destroy_img() {
    rbd rm $1
    echo "Image for $1 destroyed successfully "
}


clean_ietd_conf() {
#    set -x
    nodenames=( "$@" )
    echo $whisper | sudo -S ls > /dev/null
    myDate=`date +%y%m%d%H%M`
    sudo cp /etc/iet/ietd.conf /etc/iet/ietd.conf_$myDate
    sudo cat /etc/iet/ietd.conf > /tmp/ietd_tmp
    
    for i in ${nodenames[@]}
    do
      rbdev=`rbd showmapped|grep $i|awk '{print $5'}|awk -F / '{print $3'}`
      cat /tmp/ietd_tmp |egrep -v $i'|'$rbdev > /tmp/ietd_tmp01
      cp /tmp/ietd_tmp01 /tmp/ietd_tmp
    done
sudo cp /tmp/ietd_tmp /etc/iet/ietd.conf
sudo chown root:root /etc/iet/ietd.conf
sudo chmod 600 /etc/iet/ietd.conf
echo "Successfully removed isci-targets for ${nodenames[@]}"
}



case "$1" in 

release)
  release_rbd $2
;;

destroy) 
  destroy_img $2
;;

rm_target)
  clean_ietd_conf ${nodes[@]}
;;

remove) 
clean_ietd_conf ${nodes[@]}
for i in ${nodes[@]}
do
  release_rbd $i
  destroy_img $i
done
;;

help)
Usage
;;

*)
Usage
;;
esac
