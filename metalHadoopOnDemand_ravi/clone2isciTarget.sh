#/bin/bash

#This script will take node name from haas
#as argument and
# -- Create a clone of the golden image.
# -- map the clone to a block device.
# -- Create a isci target for booting. 
#Command to run from haas master
#ssh -A -t user@192.168.122.80 -C ". /home/user/scripts/clone2isciTarget.sh <clusterType> <nodeType> <nodeName> "

source mysecret #This file should contain the sudo password




clusterType=$1
nodeType=$2
nodeName=$3

pool="boot-disk-prototype"
rbdvar="--keyring /etc/ceph/client.henn.key --id henn"
#Golden Image name

bigdataMaster="HadoopMaster.img@HadoopMasterGoldenImage"
bigdataSlave="HadoopSlave.img@HadoopSlaveGoldenImage"

if [ $clusterType = "bigdata" ]; then
   if [ $nodeType = "master" ]; then
      goldi=$bigdataMaster
   elif [ $nodeType = "slave" ]; then
      goldi=$bigdataSlave
   fi
fi
#testing variables
#echo $nodeName $pool $whisper $goldi
#echo ""
#Creating a clone from golden image

#rbd clone boot-disk-prototype/centos-working@goldenImage --keyring /etc/ceph/client.henn.key --id henn boot-disk-prototype/$nodeName

rbd clone $pool/$goldi $rbdvar $pool/$nodeName

#Creating a block device from clone
rbdev=`echo $whisper |sudo -S rbd --keyring /etc/ceph/client.henn.key \
	--id henn map $pool/$nodeName`
#rbdev="/dev/rbd6"
#echo $rbdev

#Creating an isci target 
echo "Target iqn.2015.$nodeName"|sudo -S tee -a /etc/iet/ietd.conf

echo "        Lun 0 Path=$rbdev,Type=blockio,ScsiId=lun0,ScsiSN=lun0" \
|sudo -S tee -a /etc/iet/ietd.conf

# **Script complete** #


release_rbd() {
    echo $whisper | sudo -S ls > /dev/null
    target=`rbd showmapped | grep $1 | awk '{print $5;}'`
    echo "releasing $target"
    sudo rbd unmap $target
}

destroy_img() {
    echo "destroying image $1"
    rbd rm $1
}

clean_ietd_conf() {
    echo $whisper | sudo -S ls > /dev/null
    myDate=`date +%y%m%d%H%M`
    echo $myDate
    sudo cp /etc/iet/ietd.conf /etc/iet/ietd.conf_$myDate
    sudo cat /etc/iet/ietd.conf | egrep -v "$1|$2" | sudo -S tee /etc/iet/ietd.conf
}



#rbd ls -l |grep $nodeName

#rbd showmapped |grep $nodeName

#sudo tail -5 /etc/iet/ietd.conf


