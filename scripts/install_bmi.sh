#!/bin/bash

set -ex
sudo apt-get install -y python-pip
### Packages for BMI
sudo apt-get install -y tgt sqlite3 virtinst

git clone http://github.com/cci-moc/hil

pushd hil/
sudo apt-get install -y libvirt-bin bridge-utils ipmitool telnet apache2 libapache2-mod-wsgi python-pip qemu-kvm python-libvirt python-psycopg2 vlan net-tools icu-devtools libicu-dev libxml2-dev libxslt1-dev python-virtualenv python3-virtualenv virtualenv # For Ubuntu

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

### Setup HaaS node
haas node_register bmi_node mock moch-hostname mock-username mock-password
haas project_connect_node bmi_infra bmi_node

### Setup Node that BMI deploys to
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


### START BMI setup
git clone -b dev http://github.com/cci-moc/ims
pushd ims

### Install BMI

sudo mkdir -p /var/log/bmi/logs /etc/bmi /opt/bmi
sudo chown -R ubuntu:ubuntu /etc/bmi /var/log/bmi /opt/bmi

wget https://gist.githubusercontent.com/sirushtim/6c28b7168f9121284364e46476af0c73/raw/a9f47dbf35a891689bfc9fe34f5fdf89f6207550/bmi_config.cfg.test
cp bmi_config.cfg.test /etc/bmi/bmiconfig.cfg
cp ims/ipxe.temp /etc/bmi/ipxe.config
cp ims/mac.temp /etc/bmi/pxelinux.cfg

sudo python setup.py develop
touch /opt/bmi/bmi.db
bmi db ls
sqlite3 /opt/bmi/bmi.db "insert into project values (0, 'bmi_infra', 'bmi_network')"

# Temporary changes to get stable CI. Need to do pull request to get this fixed.
sed -i s/"app.run(host=cfg.bind_ip, port=cfg.bind_port)"/"app.run(host=cfg.bind_ip, port=int(cfg.bind_port))"/ ims/picasso/rest.py
sed -i s/"HAAS_BMI_CHANNEL = \"vlan\/native\""/"HAAS_BMI_CHANNEL = \"null\""/ ims/common/constants.py
sed -i s/"cluster = rados.Rados(rados_id=self.rid, conffile=self.r_conf)"/"cluster = rados.Rados(conffile=self.r_conf)"/ ims/einstein/ceph.py

sudo python scripts/einstein_server &
sudo python scripts/picasso_server &

sleep 5

sudo chmod 777 /etc/tgt/conf.d/

popd

bmi db ls

### Upload Image to Ceph
wget https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
rbd import cirros-0.3.0-x86_64-disk.img --dest-pool rbd

### Interface image to BMI
bmi import bmi_infra cirros-0.3.0-x86_64-disk.img

### Fin BMI setup