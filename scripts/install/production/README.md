# Running Install Script


To run the ansible-playbook to install BMI, the following steps need to be taken beforehand:

1. Install ansible:  
  a. For Ubuntu:  
      $ sudo apt-get update  
      $ sudo apt-get install software-properties-common  
      $ sudo apt-add-repository ppa:ansible/ansible  
      $ sudo apt-get update  
      $ sudo apt-get install ansible  
  b. For Centos/RHEL:  
      $ sudo yum install ansible

2. Add your hosts to the ansible hosts file (/etc/ansible/hosts)

3. Modify bmi_config.cfg to match whatever your current HIL and Ceph setup is.

4. Modify dnsmasq.conf within roles/dhcp/tasks/main.yml to match your requirements.

5. Comment out any of the roles you don't want run in site.yml

6. Run "ansible-playbook site.yml"
