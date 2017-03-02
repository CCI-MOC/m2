#!/bin/bash

git clone http://github.com/cci-moc/hil

pushd hil/

virtualenv .venv
source .venv/bin/activate
pip install -e .

cp examples/haas.cfg.dev-no-hardware ./haas.cfg

export HAAS_ENDPOINT=http://127.0.0.1:5000
export HAAS_USERNAME=haas
export HAAS_PASSWORD=secret

# Start Haas services
haas-admin db create
haas serve 5000&
haas serve_networks&

sleep 5

# Create Haas projects
haas project_create bmi_infra

### Setup HaaS mock node
haas node_register bmi_node mock moch-hostname mock-username mock-password
haas project_connect_node bmi_infra bmi_node

### Setup Mock Node that BMI deploys to
qemu-img create -f qcow2 bmi_virtual_node.qcow2 8G
sudo virt-install -n BMIVM  --description "Test BMI VM" --os-type=Linux --os-variant=rhel6 --ram=2048 --vcpus=2 --disk path=bmi_virtual_node.qcow2,bus=virtio,size=10 --pxe --network bridge:virbr0 &

sleep 10

vm_id=`sudo virsh list | grep running | awk '{ print $1 }'`
mac_address=`sudo virsh dumpxml $vm_id | grep "mac address" | awk -F\' '{print $2}'`

### Tell HaaS the mac address of the node
haas node_register_nic bmi_node bmi_port $mac_address

### Setup HaaS switch
haas switch_register bmi_switch mock moch-hostname mock-username mock-password
haas port_register bmi_switch bmi_port
haas port_connect_nic bmi_switch bmi_port bmi_node bmi_port

### Setup HaaS network
haas network_create_simple bmi_network bmi_infra

# FIN HaaS setup
deactivate
popd
