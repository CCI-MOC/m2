#!/bin/bash
source init_haas.sh
source ../mysecret

proj=$1

# ** USAGE MESSAGE ** #                                                                                           
Usage () {
    printf "Usage: $0 <project_name>\n"
    exit 1; }

[ $# -eq 0 ] && Usage

projNodes=($(haas list_project_nodes $proj |tr -d '[],"'))

##################
# CEPH image unmap/rmv

for i in ${projNodes[@]}
do
#    echo $i
#    echo "ssh -A -t user@192.168.122.34 -C '. /home/user/metalHadoopOnDemand/imageCleanup.sh remove $i '"
    ssh -A -t user@192.168.122.34 -C ". /home/user/metalHadoopOnDemand/imageCleanup.sh remove $i "
done


####################
# HaaS node release

./dynamicNodeRegeDel.sh release_nodes $proj
./dynamicNodeRegeDel.sh release_nodes $proj
./dynamicNodeRegeDel.sh release_nodes $proj


for i in ${projNodes[@]}
do
   haas node_power_cycle $i
done

echo "CLEANEDEVERYTHING"
