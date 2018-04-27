# Running Install Script


To run the ansible-playbook to install BMI, the following steps need to be taken beforehand:

1. Install ansible:  
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

2. Add your hosts to the ansible hosts file (/etc/ansible/hosts), i.e:
   # Ex 1: Ungrouped hosts, specify before any group headers.
   192.168.122.76

3. Modify bmi_config.cfg to match whatever your current HIL and Ceph setup is.

4. Modify dnsmasq.conf within roles/dhcp/tasks/main.yml to match your requirements.

5. Modify Ceph and HIL credentials in roles/bmi/tasks/main.yml to the correct username 
   and password for your configuration. This includes the CEPH_ARGS and HIL_ENDPOINT.

6. Modify the project and network from 'bmi_infra' and 'bmi_network' to the project and network
   you created within HIL.

7. Comment out any of the roles you don't want run in site.yml.

8. Run "ansible-playbook site.yml".

9. The install playbook modifies ~/.bashrc. Make sure to refresh your shell after it
   is run.
