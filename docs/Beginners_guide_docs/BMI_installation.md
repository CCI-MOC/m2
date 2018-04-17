 
**Prerequisties**: Ceph (cephargs, ceph.conf, client.bmi.key) and HIL project and network information is already available.

**Description** : Installing BMI on a machine would mean to enable a machine to provide BMI services in conjunction with Ceph and HIL (these are already configued and available as mentioned in pre-requisites). To learn more about BMI architecture and services visit https://github.com/CCI-MOC/ims/blob/master/README.md. To install BMI on a machine ansible software/ansible-playbook script is used. The script installs all the necessary software’s (on the given machine only) to orchestrate the BMI services in conjunction with Ceph and HIL. The following modifications need to be taken care of before ansible script execution. To know more about Ansible scripting/template visit http://docs.ansible.com/. 

**Pre-step** :  Modify ims/constants/common.py file so that the BMI_ADMIN_PROJECT is set to your project (HIL project) to when bootstrapping the database. Perform the following as sudo su.

1.    Get the latest Ansible playbook scripts repository from Git. The general repository is ~/ims/scripts/install/production/

 ``` 
	git clone https://github.com/CCI-MOC/ims.git 
	 
	Eg: The latest scripts at the time of documentation was PR 153.
	git fetch origin pull/153/head:pr-153
	git checkout pr-153
```

2.    Install Ansible 

a. For Ubuntu:
```
      	sudo apt-get update
      	sudo apt-get install software-properties-common
      	sudo apt-add-repository ppa:ansible/ansible
      	sudo apt-get update
      	sudo apt-get install ansible
```
b. For Centos/RHEL:
```
      	sudo yum install ansible
```

3.    Add your host to the ansible hosts file (/etc/ansible/hosts), i.e:

```
	# Ex 1: Ungrouped hosts, specify before any group headers.   
	192.168.122.76
	   
	Since in this case, we are installing on the local machine itself, the following could be done:

	# Ex 1: Ungrouped hosts, specify before any group headers.   
	localhost ansible_connection=local
```

4.    Modify the following sections in bmi_config.cfg under ~/ims   

a.    To have a new UID as follows:
```	
	[bmi]
	uid = <unique number>
	service = <true or false>

	EG:    
	[bmi]
        uid = vj-test-
        service = true
```

b.    To match your HIL setup as follows:

```
	[fs]
	id = <id in ceph>
	pool = <the ceph pool to use>
	conf_file = <location of ceph config file
	keyring = <location of ceph key ring>

	EG: 
	id = bmi
	pool = bmi
	conf_file = /etc/ceph/ceph.conf
	keyring = /etc/ceph/client.bmi.key
	(Note: Modify the id, pool name and paths accordingly.)
```

c.    To match your Ceph setup as follows:

```
	# This section is for network isolator (HIL) related config
	[net_isolator]
	url = <base url for hil>

	EG:
	[net_isolator]
	url = http://192.168.100.210:80/
	(Note: Modify the url according to your HIL endpoint accordingly)
```

5.    Modify dnsmasq.conf within roles/dhcp/tasks/main.yml. The DHCP range and interface needs to be changed accordingly to match your requirements (below is an example).

```
	- name: Add DHCP configuration to dnsmasq.conf
		lineinfile:
          path: /etc/dnsmasq.conf
	  line: "{{ item }}"
          become: true
          with_items:
	      - 'interface=eth2'
	      - 'dhcp-range=10.10.10.50,10.10.10.100,7d'
	      - 'dhcp-boot=pxelinux.0'
	      - 'enable-tftp'
	      - 'tftp-root=/var/lib/tftpboot'
	      - 'dhcp-userclass=set:ENH,iPXE'
```

Note : Also configure the interface (eth2 in the above ex) to have a gateway IP related to the range of IPs chosen above. Considering the above case, ifcfg-eth2 could have static IP of say 10.10.10.1.


6.    In roles/bmi/tasks/main.yml:

a.    Modify Ceph and HIL credentials in to the the correct username and password for your configuration. This includes the CEPH_ARGS and HIL_ENDPOINT (below is an example).

```
	- name: Add Ceph and HIL credentials to bashrc
		lineinfile:
	  path: ~/.bashrc
	  line: "{{ item }}"
	  become: true
	  with_items:
	      - 'export CEPH_ARGS="--keyring /etc/ceph/client.bmi.key --id bmi --pool bmi"'
	      - 'export HIL_USERNAME=vj'
	      - 'export HIL_PASSWORD=redhat'
	      - 'export HIL_ENDPOINT="http://192.168.100.210:80"'
	      - 'export BMI_CONFIG=/etc/bmi/bmiconfig.cfg'

```

b.    Modify the project project and network from 'bmi_infra' and 'bmi_network' to the project and network you created within HIL (below is an example).

```
	- name: Bootstrap the database
          command: "{{ item }}"
	  environment:
	      HIL_USERNAME: vj
	      HIL_PASSWORD: redhat
	   with_items:
	       - bmi db ls
	       - sqlite3 /etc/bmi/bmi.db "insert into project values (1, 'vj', 'bmi-provision-vj')"
	         when: db.stat.size == 0
```

7.    Comment out any of the roles that you don’t want to execute in site.yml.

8.    Run ansible-playbook site.yml.
   
 ```    
       ansible-playbook site.yml
```

9.   The install playbook modifies ~/.bashrc. Make sure to refresh your shell after it is run.


Possible errors one may face:
------------------------------


1.    

```
fatal: [localhost]: FAILED! => {"changed": false, "cmd": "/usr/bin/git clone --origin origin https://github.com/fujita/tgt /home/vj/ims/scripts/install/production/tgt", "msg": "fatal: could not create work tree dir '/home/vj/ims/scripts/install/production/tgt'.: Permission denied", "rc": 128, "stderr": "fatal: could not create work tree dir '/home/vj/ims/scripts/install/production/tgt'.: Permission denied\n", "stderr_lines": ["fatal: could not create work tree dir '/home/vj/ims/scripts/install/production/tgt'.: Permission denied"], "stdout": "", "stdout_lines": []}[WARNING]: Could not create retry file '/home/vj/ims/scripts/install/production/site.retry'.         [Errno 13] Permission denied: u'/home/vj/ims/scripts/install/production/site.retry'

```

Possible reasons: Not executing as sudo.


2.    

```
Error 4 \nwarning: failed to load external entity \"http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl\" 
```

Possible reasons: The sourceforge site could be offline or down. Could try again after a while.
(Note: This site is frequently known to be down!. Could think about having these docs stored locally.)

