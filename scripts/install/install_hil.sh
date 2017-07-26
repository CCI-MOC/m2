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

cp examples/hil.cfg.dev-no-hardware ./hil.cfg

export HIL_ENDPOINT=http://127.0.0.1:5000
export HIL_USERNAME=hil
export HIL_PASSWORD=secret

# Start HIL services
hil-admin db create
hil serve 5000&
hil serve_networks&

sleep 5

# Create HIL projects
hil project_create bmi_infra

### Setup HIL mock node
hil node_register bmi_node mock moch-hostname mock-username mock-password
hil project_connect_node bmi_infra bmi_node

### Tell HIL the mac address of the node
hil node_register_nic bmi_node bmi_port "00:00:00:00:00:00"

### Setup HIL switch
hil switch_register bmi_switch mock moch-hostname mock-username mock-password
hil port_register bmi_switch gi1/0/1
hil port_connect_nic bmi_switch gi1/0/1 bmi_node bmi_port

### Setup HIL network
hil network_create_simple bmi_network bmi_infra

# FIN HIL setup
deactivate
popd
