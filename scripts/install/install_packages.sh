#!/bin/bash

# Determine Vendor

OS = $(lsb_release -i -s)

if [[ $OS =~ "Ubuntu" ]]; then
    sudo apt-get install git

    ### Packages for HIL
    sudo apt-get install -y libvirt-bin bridge-utils \
        ipmitool telnet apache2 libapache2-mod-wsgi python-pip \
        qemu-kvm python-libvirt python-psycopg2 vlan net-tools \
        icu-devtools libicu-dev libxml2-dev libxslt1-dev \
        python-virtualenv python3-virtualenv virtualenv

    ### Packages for BMI
    sudo apt-get install -y tgt tgt-rbd sqlite3 virtinst
else
    die "Support for $OS is on the way"
fi

# TODO: Install packages for RHEL/CentOS
