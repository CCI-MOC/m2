# BMI


## Installation

This document describes how to setup BMI. We officially support RHEL and it's
variants, but it may also work on ubuntu (Debian) like OSes. 

### Prerequisite Softwares

BMI requires the following non python dependencies. 

#### Ceph Client
Ceph is a distributed object store and file system designed for performance and scalibility. 
For more information, visit the [official website](http://docs.ceph.com/docs/master/start/)

To install ceph client:
```
yum install ceph-common
```

#### iSCSI Server
We recommend using the TGT iSCSI variant as its BMI driver is more stable.   
You can install it on RHEL family with the following set of commands:  

```
git clone https://github.com/fujita/tgt.git
cd tgt

yum install -y make
yum install -y gcc
** delete install doc from Makefile if problem occurs in the next three steps
make CEPH_RBD=1 clean
make CEPH_RBD=1
make CEPH_RBD=1 install


cp scripts/tgtd.service /usr/lib/systemd/system/
systemctl daemon-reload
# this is to check if tgtd has been made as a daemon
systemctl list-unit-files | grep -i tgt

# TGT uses port 3260 by defualt, so make sure you open it. 
iptables -I INPUT -p tcp -m tcp --dport 3260 -j ACCEPT
service iptables save

systemctl start tgtd
chkconfig tgtd on
systemctl status tgtd
```

For more information visit their [website](http://stgt.sourceforge.net/) and the [Quick Start Guide](https://fedoraproject.org/wiki/Scsi-target-utils_Quickstart_Guide)

#### DHCP server
We support `dnsmasq` for this. 

`$ yum install dnsmasq`

For more information about dnsmasq, you can look at the [wiki](https://wiki.debian.org/HowTo/dnsmasq)

#### Hardware Isolation Layer (HIL)

To setup HIL, you can read the [HIL documentation](http://hil.readthedocs.io/en/latest/)

### Installling
* Clone this repository to your home folder and change to `dev` branch
```
$ git clone https://github.com/CCI-MOC/ims
$ git checkout dev
```
* Run setup.py and install python-cephlibs
```
$ sudo python setup.py install
$ pip install python-cephlibs
```

That's it. Installation is done!
***

## Configuration

The template for the config is [here](https://github.com/CCI-MOC/ims/blob/dev/bmi_config.cfg)
It describes the purpose and how to fill each section in it. 

## Running BMI

### Einstein  

Einstein is the backend that does the operations. 

First export the path of BMI config file to environment variable (BMI_CONFIG)

```
$ export BMI_CONFIG=/home/bmi/bmi_config.cfg
```

Then open a screen (Open a fresh screen always) and start einstein
```
$ screen
$ einstein_server (In screen)
```

Should see some lines stating einstein is running then hit Ctrl+A+D.  

Einstein is running!

### Picasso

Picasso is the frontend that handles the API calls. 

Should export like einstein. Then open screen (Open a fresh screen always) and start picasso
```
$ screen
$ picasso_server (In screen)
```

Should see one line stating that Picasso is running  

Picasso is running!!

### Bootstrapping the Database

Since we dont have installation script or command that will create the admin user, it must be done manually.

Do
```
sqlite3 <db>
insert into project values(1,'bmi_infra','provision');
.quit
```

The above command will insert the admin user that is bmi_infra
