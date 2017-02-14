# BMI

The Bare Metal Imaging (BMI) is a core component of the Massachusetts Open Cloud and a image management system(ims) that  
* provisions numerous nodes as quickly as possible while preserving support for multitenancy using Hardware as a Service (HaaS) and  
* introduces the image management techniques that are supported by virtual machines, with little to no impact on application performance.  

***
## Installation

This document describes how to setup BMI

### Prerequisite Softwares

BMI requires the following non python dependencies. 

#### Ceph Client
Ceph is a distributed object store and file system designed for performance and scalibility. 
For more information, visit the [official website](http://docs.ceph.com/docs/master/start/)

You can follow [this guide](http://palmerville.github.io/2016/04/30/single-node-ceph-install.html) 
to setup a ceph client on a VM

#### iSCSI Server
We recommend using the TGT iSCSI variant as its driver is more stable.   
You can install it with the following command:  
`$ yum install scsi-target-utils`

For more information visit their [website](http://stgt.sourceforge.net/) and the [Quick Start Guide](https://fedoraproject.org/wiki/Scsi-target-utils_Quickstart_Guide)

#### DHCP server
You can setup `dnsmasq` for this. 

* On ubuntu:
`$ sudo apt-get install dnsmasq`

* On CentOS:
`$ yum install dnsmasq`

For more information about dnsmasq, you can look at the [wiki](https://wiki.debian.org/HowTo/dnsmasq)

#### TFTP Server
##### On ubuntu:
* Install these packages:  `$ sudo apt-get install xinetd tftpd tftp`

* Create `/etc/xinetd.d/tftp` and put this entry  
  
```
service tftp
{
protocol        = udp
port            = 69
socket_type     = dgram
wait            = yes
user            = nobody
server          = /usr/sbin/in.tftpd
server_args     = /tftpboot
disable         = no
}
```
##### On CentOS:
* Install these packages:  `$ sudo yum install tftp tftp-server xinetd`
* Modify `/etc/xinetd/tftp` as shown below  

```
service tftp
{
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = root
        server                  = /usr/sbin/in.tftpd
        server_args             = /tftpboot
        disable                 = no
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
```

* Create a folder `/tftpboot` this should match whatever you gave in `server_args.` mostly it will be `tftpboot`:
  
```
$ sudo mkdir /tftpboot
$ sudo chmod -R 777 /tftpboot
$ sudo chown -R nobody /tftpboot
```
  
* Restart the `xinetd` service:  `$ sudo service xinetd restart`



The TFTP server should be up and running. For more information click [here](http://askubuntu.com/questions/201505/how-do-i-install-and-run-a-tftp-server)

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
## Running

### Creating Tunnel (Only for internal purposes)

Since HIL is typically bound to localhost interface, we need to create a ssh reverse tunnel from BMI VM (Some port) to HIL's 127.0.0.1:80.

The following command needs to be executed on HIL.

```
$ ssh -fNR <port on BMI VM>:127.0.0.1:80 <username>@<bmi vm ip> 
```
The general default port we use is 6500.  
For PRB we made 2 tunnels

* HIL's 127.0.0.1:80 -> moc02's 6500
* moc02's 6500 -> BMI VM's 6500

For Northeastern and Engage1 just the regular tunnel.

### Configuration

The template for the config is [here](https://github.com/CCI-MOC/ims/blob/dev/bmi_config.cfg)

This section describes each config section along with sample  

**bmi section**  
* uid is used to prevent clashing of BMIs that use the same Ceph Pool. It is the responsibility of the admin to ensure that uid is unique.
* service should be set to True if BMI is deployed as a service. Set it to False for now as there are some glitches.
```
# this section is for basic bmi settings
[bmi]
# uid is given so that images dont clash in ceph pool
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
Tells which Filesystem to load (Will be removed)
* ceph should be set to True since we don't support any other Filesystem.
```
# This section is to denote which filesystem is being used
[filesystem]
ceph = True
```  

**Ceph Section**
* id is the ceph id which has access to the pool
* pool is the ceph pool to use for storing images
* conf_file is the path to the Ceph conf file
* keyring is the path to the keyring file
```
# This section is for ceph config
[ceph]
id = bmi
pool = bmi
conf_file = /etc/ceph/ceph.conf
keyring = /etc/ceph/bmi.key
```  

**Hil Section**
* url is the HTTP endpoint for HIL
```
# This section is for haas related config
[haas]
url = http://localhost:3241/
```  

**iscsi section**
* ip is the ip of iscsi server on the provisioning network
* password is the sudo password for the VM (Will be removed)
```
# This section is for iscsi related config
[iscsi]
ip = <ip of iscsi server>
password = <sudo password for iscsi_update script>
```  

**rpc section**
* name_server ip and port is the RPC NameServer's IP and Port
* rpc_server ip and port is the RPC Server's IP and Port (The end which calls einstein)
```
# this section is for rpc server config
[rpc]
name_server_ip = 127.0.0.1
name_server_port = 10000
rpc_server_ip = 127.0.0.1
rpc_server_port = 10001
```  

**tftp section**
* pxelinux_url is the path to the pxelinux.cfg folder
* ipxe_url is the path to the location where ipxe files should be created (root of tftpboot folder)
```
# this section is for specifying tftp settings
[tftp]
pxelinux_url = /var/lib/tftpboot/pxelinux.cfg
ipxe_url = /var/lib/tftpboot/
```  
**http section**
* bind_ip and port is the ip and port picasso should bind to
```
# this section is for http config
[http]
bind_ip = 127.0.0.1
bind_port = 8000
```  
**logs section**
* url is the folder where logs should be generated
* debug enables debug logs
* verbose prints logs to screen
```
# this section is for logs
[logs]
url = /home/bmi/logs/
debug = False
verbose = False
```

### Einstein  

First export the variable BMI_CONFIG

```
$ export BMI_CONFIG=/home/bmi/bmiconfig.cfg
```

Then open a screen (Open a fresh screen always) and start einstein
```
$ screen
$ einstein_server (In screen)
```

Should see some lines stating einstein is running then hit Ctrl+A+D.  

Einstein is running!!

### Picasso

Should export like einstein. Then open screen (Open a fresh screen always) and start picasso
```
$ screen
$ picasso_server (In screen)
```

Should see one line stating that Picasso is running  

Picasso is running!!

### Initing DB

Since we dont have installation script or command that will create the admin user, it must be done manually.

Do
```
sqlite3 <db>
insert into project values(1,'bmi_infra','provision');
.quit
```

The above command will insert the admin user that is bmi_infra