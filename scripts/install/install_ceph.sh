#!/bin/bash

set -ex

# Single node ceph install with loopback devices.

node_name=`cat /etc/hostname`

# You may have to change this to suit your environment.
ip_addr=`ifconfig | grep 192 | awk '{ print $2}' | awk -F: '{ print $2 }'`
sudo sh -c "echo '$ip_addr localhost $node_name' >> /etc/hosts"

sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ceph-deploy

ceph-deploy new $node_name
echo -e "osd pool default size = 2\nosd crush chooseleaf type = 0" >> ceph.conf
ceph-deploy install $node_name
ceph-deploy --overwrite-conf mon create-initial

truncate -s 10000M sparse-file0
truncate -s 10000M sparse-file1
truncate -s 10000M sparse-file2

sudo losetup /dev/loop0 sparse-file0
sudo losetup /dev/loop1 sparse-file1
sudo losetup /dev/loop2 sparse-file2

ceph-deploy osd prepare $node_name:loop0
ceph-deploy osd prepare $node_name:loop1
ceph-deploy osd prepare $node_name:loop2

ceph-deploy osd activate $node_name:/dev/loop0p1
ceph-deploy osd activate $node_name:/dev/loop1p1
ceph-deploy osd activate $node_name:/dev/loop2p1

ceph-deploy admin $node_name
sudo chmod +r /etc/ceph/ceph.client.admin.keyring

ceph -s

ceph-deploy rgw create $node_name
ceph-deploy mds create $node_name


### TEST

# sudo pkill -f ceph
# sudo losetup -d /dev/loop2 /dev/loop1 /dev/loop0
# sudo rm /etc/ceph/ceph.conf
