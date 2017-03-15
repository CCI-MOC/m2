#!/bin/bash

user=`whoami`

sudo mkdir /opt/hil
sudo chown $user:$user /opt/hil
sudo chmod 775 /opt/hil

git clone http://github.com/cci-moc/hil /opt/hil

pushd /opt/hil/

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

### Tell HaaS the mac address of the node
haas node_register_nic bmi_node bmi_port "00:00:00:00:00:00"

### Setup HaaS switch
haas switch_register bmi_switch mock moch-hostname mock-username mock-password
haas port_register bmi_switch bmi_port
haas port_connect_nic bmi_switch bmi_port bmi_node bmi_port

### Setup HaaS network
haas network_create_simple bmi_network bmi_infra

# FIN HaaS setup
deactivate
popd
