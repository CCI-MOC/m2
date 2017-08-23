#!/bin/bash

set -ex

# Single node ceph install with loopback devices.

node_name=`cat /etc/hostname`

# You may have to change this to suit your environment.
if [[ -f /etc/redhat-release ]]; then
    ip_addr=`sudo ifconfig | grep 192 | awk '{ print $2}'`
    sudo yum -y remove librados2 librbd1
else
    ip_addr=`sudo ifconfig | grep 192 | grep -v 122 | awk '{ print $2}' | awk -F: '{ print $2 }'`
fi
sudo sh -c "echo '$ip_addr localhost $node_name' >> /etc/hosts"

ceph-deploy new $node_name
echo -e "public_network = 192.168.1.0/24\nosd pool default size = 2\nosd crush chooseleaf type = 0" >> ceph.conf
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

# Note/TODO:
# This ceph is not presistent across reboots.
# we have to make the loopback devices again, re-read the partition table
# (`partprobe /dev/loopx`) and then "ceph activate all osds".
### TEST

# sudo pkill -f ceph
# sudo losetup -d /dev/loop2 /dev/loop1 /dev/loop0
# sudo rm /etc/ceph/ceph.conf
