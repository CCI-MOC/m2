#!/bin/bash
source init_haas.sh
now=$(date +"%T")
echo "Script start : $now"

proj=$1
num_nodes=$2

# ** USAGE MESSAGE ** #                                                                                           
Usage () {
    printf "Usage: $0 <project_name> <num_of_nodes>\n"
    exit 1; }

[ $# -eq 0 ] && Usage


####################
# HaaS node registration

./dynamicNodeRegeDel.sh register_nodes $proj $num_nodes


now=$(date +"%T")
echo "HaaS init Finish : $now"
###################################################
# CEPH cloning 

projNodes=($(haas list_project_nodes $proj |tr -d '[],"'))
masterNode=${projNodes[0]}
## echo $masterNode
## set -x
echo "cloning images in CEPH"
## echo "ssh -A -t user@192.168.122.34 -C '/bin/bash -x /home/user/metalHadoopOnDemand/clone2isciTarget.sh bigdata master $masterNode '"
ssh -A -t user@192.168.122.34 -C "/bin/bash  /home/user/metalHadoopOnDemand/clone2isciTarget.sh bigdata master $masterNode "
ssh -A -t user@192.168.122.34 -C "/home/user/metalHadoopOnDemand/chrootClonedImage.sh restart_ietd"
for i in ${projNodes[@]:1}
do
##   echo $i
##    echo "ssh -A -t user@192.168.122.34 -C '. /home/user/metalHadoopOnDemand/clone2isciTarget.sh bigdata slave $i '"
    ssh -A -t user@192.168.122.34 -C ". /home/user/metalHadoopOnDemand/clone2isciTarget.sh bigdata slave $i "
##    ssh -A -t user@192.168.122.34 -C "/home/user/metalHadoopOnDemand/chrootClonedImage.sh restart_ietd"
done

ssh -A -t user@192.168.122.34 -C "/home/user/metalHadoopOnDemand/chrootClonedImage.sh restart_ietd"
####################
# chrooting and editing (pre and post install scripts)
#echo "mounting master"
#ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh mount_node $masterNode"
#ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh edit_node $masterNode"

#echo "unmounting master $masterNode"
#ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh unmount_node $masterNode"
now=$(date +"%T")
echo "CEPH cloning Finish : $now"


haas node_power_cycle $masterNode

for i in ${projNodes[@]:1}
do
#    echo "mounting $i"
#    ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh mount_node $i"
#    #edit
#    ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh edit_node $i"
#    #unmount
#    echo "unmounting $i"
#    ssh -A -t user@192.168.122.34 -C "/bin/bash -x /home/user/metalHadoopOnDemand/chrootClonedImage.sh unmount_node $i"
    haas node_power_cycle $i
done

now=$(date +"%T")
echo "PowerCycle Finish : $now"

show_node_status () {
    #set -x
    nodeId=`echo $1 | cut -d"-" -f2`
    if [[ $nodeId < 10 ]]
    then nodeId=`echo $nodeId | cut -d"0" -f2`
    fi
    nodeIp=192.168.29.$nodeId

    a=0
    export x=`ssh -A -t user@192.168.122.34 -C "nmap $nodeIp -PN -p ssh"|egrep "open|closed|filtered" |awk '{ print $2 '}`
    if [[ $x == "open" ]]
    then echo "SUCCESS::$1"; let a=0
    else let a=1
    fi
    return $a
}


show_node_status $masterNode
x=`echo $?`
while [ $x != 0 ]
do
    show_node_status $masterNode
    x=`echo $?`
    
done
echo "MASTER:$masterNode"


for i in ${projNodes[@]:1}
do
    show_node_status $i
    x=`echo $?`
    while [ $x != 0 ]
    do
	show_node_status $i
	x=`echo $?`
	
    done
    echo "SLAVE:$i"
done


now=$(date +"%T")
echo "FINISHETIME:$now"


masterId=`echo $masterNode | cut -d"-" -f2` 
if [[ $masterId < 10 ]]
    then masterId=`echo $nodeId | cut -d"0" -f2`
fi

masterHostname="bigdata$masterId.moc.ne.edu"
masterIp="192.168.29.$masterId"
ssh -A -t user@192.168.122.34 -C "/bin/bash /home/user/metalHadoopOnDemand/postScriptMaster.sh $masterIp $masterHostname"


for i in ${projNodes[@]:1}
do
(    slaveId=`echo $i | cut -d"-" -f2` 
    if [[ $slaveId < 10 ]]
    then slaveId=`echo $nodeId | cut -d"0" -f2`
    fi
    slaveIp="192.168.29.$slaveId"
    ssh -A -t user@192.168.122.34 -C "/bin/bash /home/user/metalHadoopOnDemand/postScriptSlave.sh $slaveIp $masterHostname" ) &

done
wait

now=$(date +"%T")
echo "BIGDATATIME:$now"
