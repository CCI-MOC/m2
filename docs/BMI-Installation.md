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

This section describes each config section along with sample  

**bmi section**  
* uid is used to prevent clashing of BMIs that use the same Ceph Pool. It is the responsibility of the admin to ensure that uid is unique.
* service should be set to True if BMI is deployed as a service. Set it to False for now as there are some glitches.
```
# this section is for basic bmi settings
[bmi]
uid = 5
service = False
```  

**db section**  
* url is the path of the sqlite db
```
# this section is for db settings
[db]
url = /home/user/bmi.db
```  

**filesystem section**  
Tells which Filesystem to use (right now, we only support ceph)

* id is the ceph id which has access to the pool
* pool is the ceph pool to use for storing images
* conf_file is the path to the Ceph conf file
* keyring is the path to the keyring file
```
# This section is filesystem related config
[fs]
id = bmi
pool = bmi
conf_file = /etc/ceph/ceph.conf
keyring = /etc/ceph/bmi.key
```

**Driver section**

* iscsi is the iscsi driver to load
* fs is the filesystem to use
* net_isolator is the name of the network isolator to use.
It connects the node to a network on which BMI can provision. We require this to have
multi-tenancy while provisioning (securely). We use HIL for network
isolation. [Link to HIL](http://hil.readthedocs.io/en/latest/)
```

[driver]
fs = ims.einstein.fs.ceph.driver
net_isolator = <default>
iscsi = ims.einstein.tgt.driver
```
**Network Isolator section**

* This section is for network isolated related configuration

```
[net_isolator]
url = <base url for network isolator>
```

**iscsi section**
* ip is the ip of iscsi server on the provisioning network
* password is the sudo password for the VM (Will be removed)
```
# This section is for iscsi related config
[iscsi]
ip = 127.0.0.1
password = password
```  

**rpc section**
* name_server is the ip and port Name Server binds to
* rpc_server is the ip and port RPC Server binds to (The end which calls einstein)
```
# this section is for rpc server config
[rpc]
name_server_ip = 127.0.0.1
name_server_port = 10000
rpc_server_ip = 127.0.0.1
rpc_server_port = 10001

checkout [pyro](https://pypi.python.org/pypi/Pyro4) to know more about it.
```  

**tftp section**
* pxelinux_path is the path to the pxelinux.cfg folder
* ipxe_path is the path to the location where ipxe files should be created (root of tftpboot folder)
```
# this section is for specifying tftp settings
[tftp]
pxelinux_path = /var/lib/tftpboot/pxelinux.cfg
ipxe_path = /var/lib/tftpboot/
```  
**API server section**
* bind_ip and port is the ip and port picasso should bind to
```
[rest_api]
bind_ip = 127.0.0.1
bind_port = 8000
```  
**logs section**
* path is the folder where logs should be generated
* debug enables debug logs
* verbose prints logs to screen
```
# this section is for logs
[logs]
path = /home/bmi/logs/
debug = False
verbose = False
```
## Running BMI

### Einstein  

Einstein is the backend that does the operations. 

First export the path of BMI config file to environment variable (BMI_CONFIG)

```
$ export BMI_CONFIG=/home/bmi/bmiconfig.cfg
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
