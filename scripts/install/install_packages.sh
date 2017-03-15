#!/bin/bash

set -x

die() { echo "$@" 1>&2 ; exit 1; }

# Determine Vendor

OS=$(lsb_release -i -s)

if [[ $OS =~ "Ubuntu" ]]; then
    sudo apt-get update

    # Package for script
    sudo apt-get install git

    # Package for Ceph
    sudo apt-get install -y ceph-deploy

    ### Packages for HIL
    sudo apt-get install -y libvirt-bin bridge-utils \
        ipmitool telnet apache2 libapache2-mod-wsgi python-pip \
        qemu-kvm python-libvirt python-psycopg2 vlan net-tools \
        icu-devtools libicu-dev libxml2-dev libxslt1-dev \
        python-virtualenv python3-virtualenv virtualenv

    ### Packages for BMI
    sudo apt-get install -y tgt tgt-rbd sqlite3 virtinst
elif [[ -f /etc/redhat-release ]]; then
    # Assume RHEL is registered with subscription-manager
    # Subscription manager stuff
    pool_id=`sudo subscription-manager list --available | grep -A15 "Red Hat Ceph Storage" | grep "Pool ID" | awk '{ print $3 }'`
    sudo subscription-manager attach --pool=$pool_id
    sudo subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-optional-rpms --enable=rhel-7-server-rhceph-1.2-calamari-rpms --enable=rhel-7-server-rhceph-1.2-installer-rpms --enable=rhel-7-server-rhceph-1.2-mon-rpms --enable=rhel-7-server-rhceph-1.2-osd-rpms

    # Packages for script
    sudo yum install -y git gcc wget cpan make 

    # Packages for Ceph
    sudo yum install -y ceph-deploy

    # Headers for tgt source compilation
    sudo yum install -y librbd1-devel librados2-devel

    ## Install tgt from source
    git clone https://github.com/fujita/tgt
    pushd tgt/

    sudo make CEPH_RBD=1 clean
    sudo make CEPH_RBD=1
    sudo make CEPH_RBD=1 install

    sudo cp scripts/tgtd.service /usr/lib/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl list-unit-files | grep -i tgt

    sudo iptables -I INPUT -p tcp -m tcp --dport 3260 -j ACCEPT
    sudo service iptables save

    sudo systemctl start tgtd
    sudo chkconfig tgtd on
    sudo systemctl status tgtd

    popd

    # Install packages for HIL
    sudo yum install -y epel-release bridge-utils  gcc  httpd  ipmitool libvirt \
	libxml2-devel  libxslt-devel  mod_wsgi net-tools python-pip python-psycopg2 \
	python-virtinst python-virtualenv qemu-kvm telnet vconfig virt-install

else
    die "Support for $OS doesn't exist yet"
fi
