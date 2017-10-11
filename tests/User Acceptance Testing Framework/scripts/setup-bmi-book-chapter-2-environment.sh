#!/bin/bash

git clone https://github.com/CCI-MOC/ims.git
cd ims
git fetch origin pull/60/head:pr-60
git checkout pr-60
cd scripts/install/
export IP_ADDRESS=`ifconfig | grep inet | cut -f10 -d' ' | head -n1`
echo -e "public_network = $IP_ADDRESS\nosd pool default size = 2\nosd crush chooseleaf type = 0" >> ceph.conf

cp /etc/hostname .
cat /etc/hostname | cut -f1 -d'.' > hostname
sudo cp hostname /etc
./install.sh
source bmi_userrc.sh
cd ~/ims
source .bmi_venv/bin/activate


