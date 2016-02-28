#!/usr/bin/bash
# Title		:  dynamicNodeRegeDel.sh
# Created	:  2015/11/08
# Usage		:  ./dynamicNodeRegeDel.sh help
# Depends on 	:  init_haas.sh
# Prerequisite	:  Haas project, network and headnode should exist
# Description	:  
#   register_nodes -- registers nodes to the project
#		   -- Connects to the network
#		   -- powercycles them
#   release_nodes  -- Releases all nodes from the project
#   show_nodes	   -- Gives details about each node in the project
#   status	   -- Updates to the status of nodes while they are booting.
#
# Team		: Sahil, Ata, Jason, Ugur, Ravi
#
##############################################################################



# ** Section 1:  **
# Fetch the free nodes from HaaS and remove "cisco-05" from the list

source init_haas.sh
proj=$2

freeNodes=($(haas list_free_nodes |tr -d '[],"'))
node="cisco-05" #it is a bad node
#freeNodes=()
all=${freeNodes[@]}

for i in ${!freeNodes[@]}
do
if [[ "${freeNodes[$i]}" = "${node}" ]]
then 
    unset freeNodes[$i]
fi
done
echo 

newall=${freeNodes[@]}

# ** End of section 1 ** #

# ** USAGE MESSAGE ** #
Usage () { 
printf "Usage: $0   [register_nodes <project name> <no_of_nodes>] \
       \n\t\t\t\t [release_nodes <project name> ]\
       \n\t\t\t\t [show_nodes <project name> ]\
       \n\t\t\t\t [status <project_name> ]\n" 
exit 1; }

[ $# -eq 0 ] && Usage 


#{ printf "Usage: $0 <project name>  [release_nodes] \
#		\n\t\t\t\t <project name> [register_nodes <no_of_nodes>]\
#		\n\t\t\t\t <project name> [show_nodes]\n"; exit 1; }



# ** RELEASE NODES FROM A PROJECT ** 
release_nodes() {
projNodes=($(haas list_project_nodes $proj |tr -d '[],"'))

if [[ ${#projNodes[@]} == 0 ]]
then 
    echo "The node-list is empty. Nothing to release. Aborting !! "
    exit 1
else
    echo "Releasing all nodes from Project: $proj "
    for i in ${projNodes[@]}
    do
      haas node_detach_network $i enp130s0f0 bmi-provision
      #haas node_detach_network $i enp130s0f0 nat-public
      sleep 2
      haas project_detach_node $proj $i > /dev/null
   done
fi

projNodes01=($(haas list_project_nodes $proj |tr -d '[],"'))
if [[ ${#projNodes01[@]} == 0 ]]
then
    echo "All nodes successfully released from Project:$proj"
else
   echo "Error: All nodes not released. Please check manually. "
   exit 1
fi
}


# ** REGISTER NODES FROM FREE LIST TO THE PROJECT **
# eg. /dynamicNodeRegeDel.sh register_nodes 4 
# will check if there are 4 nodes available in free pool
# if there exists enough nodes, it will register them with the 
# project, or it will report otherwise.


register_nodes () {
[ $# -eq 0 ] && { printf "Usage: $0 register_nodes <project name> <no_of_nodes> \n"; exit 1; }
qty=$2
if [ "$qty" -le "${#freeNodes[@]}" ]
then
    echo "Adding $qty nodes to project $proj"
    allocNodes=${freeNodes[@]:0:$qty}
    for i in ${allocNodes[@]}
    do
  	haas project_connect_node $proj $i > /dev/null
  	haas node_connect_network $i enp130s0f0 bmi-provision vlan/native
    done
    haas list_project_nodes $proj
else
	echo "Sorry, we have only  ${#freeNodes[@]} nodes in free pool"
fi

}

# ** Show information about nodes registered with project
# It will show details about each node registered with the project.

show_node_info () {
projNodes=($(haas list_project_nodes $proj |tr -d '[],"'))
if [[ ${#projNodes[@]} == 0 ]]
then 
    echo "The node-list is empty "
else
    echo "Details about each Node: "
    for i in ${projNodes[@]}
    do
	haas show_node $i
    done
    echo "Total Nodes: ${#projNodes[@]} "
    echo "Allocated to Project: $proj "

fi

}

# Still needs work. Need to talk to Ata about this. 

# this has to know the master node IP address, we have a fixed IP address for each node
# so it has to know whcih node is the master, this is where we define the master 
show_node_status () {
sleep 5
for i in 12 13 14  
do
y=192.168.29.$i
a=0
#print $y
#let x=`ssh -A user@192.168.122.34 -C "ping -c5 $y"|grep "packet loss"|awk '{ print $4 '}`
export x=`ssh -A user@192.168.122.34 -C "nmap $y -PN -p ssh"|egrep "open|closed|filtered" |awk '{ print $2 '}`
#echo "x = $x "
if [[ $x == "open" ]] 
then echo " Cisco-$i: Booted successfully !! "; let a=0
else echo " Cisco-$i: Not Booted "; let a=1
fi
done
echo " "
return $a

}


case  "$1"  in

register_nodes) 
  register_nodes $2 $3
;;

release_nodes) 
  release_nodes
;;

show_nodes) 
  show_node_info
;;

status)
show_node_status
x=`echo $?`
while [ $x != 0 ]
do
show_node_status
x=`echo $?`
done
echo "All nodes booted successfully. "
;;

*)
Usage
;;
esac
