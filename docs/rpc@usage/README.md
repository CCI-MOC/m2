# RPC

### Overview:  
This is the RPC server, name server and client programs to be run for the iSCSI.

### Additional packages required:  
These programs requires Pyro4 python package. The command to do so is as follows:  


    pip install Pyro4  

This package allows to build applications in which objects can talk to each other
over the network. 
  

### Folder contents:  
1. rpcserver.py - This is the server program that processes the client request.  
2. nameserver.py - This is the name server program, the server registers the object 
                   with the name server and the client looks up for the object or
                   service.  
3. rpcclient.py - This file is the client program that needs to be run to make a 
                   a request to the main server.
4. test.py  - This file is the python program that tests the MainSever class
                   in the mainserver.py file by creating objects of the class, and
                   testing the actual output of the methods against the desired output.  
5. nameserver-daemon.sh - This file runs the nameserver.py file as a daemon. This allows  
                          the nameserver.py file to run as long as the system is not rebooted.  
6. rpcserver-daemon.sh - This file runs the rpcserver.py file as a daemon. This allows  
                          the rpcserver.py file to run in background as long the system is not rebooted.
  
### How to run the programs:  
The programs should be run in the following sequence:  
  
**1. nameserver.py:**  
  
The nameserver.py file needs to be run first. The name server program listens for any
server registering their objects.  
  
To run the name server simply run the python program:  
  
    python nameserver.py  
  
This creates a name server. The name server is binded to a IP Address that can be reached
by other systems on the network. This ip address is mentioned in nameserver.py file to the
variable name_server_address.
  
This ip address should be reachable by name server and clients.  
  
NOTE: This file is now executed by running the nameserver-daemon shell script.
  
**2. rpcserver.py:**   
  
The mainserver.py file needs to be executed once the name server is running and listening for
the server objects. The main server is binded to a IP Address as well. This address is provided
to the Pyro server through config.HOST variable.  
  
The IP Address for the main server is to be entered in the mainserver.py file by initializing the 
 Pyro4.config.HOST in the __init__().
  
This IP Address should be reachable by name server and clients.   
  
NOTE: The name server and main server can be run on the same system as well. Still the both this 
      system will need to be configured with ip addresses the client program can reach.  
      This file is now executed by running the rpcserver-daemon shell script.
  
**3. rpcclient.py:**  
  
The mainclient.py file needs to be executed with the appropriate arguments everytime a request to
the server is to be made.  
  
The example command looks as follows:  
    
    python rpcclient.py provision/detach_node/create_snapshot/list_all_images... arg1 arg2 .....
  
where,  
     provision/detach_node/create_snapshot/list_all_images/... :- These are the methods provided by the server.  
     arg1 arg2 ... :- Is the arguments that needs to be provided for a script to run.  
  
**4. test.py:**  
The test.py file uses the Unittest class of python to test the behavior of the rpcclient.py program.  
  
This is should be executed as a normal python program, i.e  

    python test.py  
  
**5. nameserver-daemon.sh:**  
The nameserver-daemon.sh file needs to be present in the /etc/init.d folder on the server machine. This file should be  
executed with root privileges as it creates and accesses the nameserver.pid file from the /var/run directory.  

Run the following commands to give nameserver.py the appropriate access rights. Then copy the daemon shell script to the /etc/init.d folder. Then assign the daemon file with execution permission.  
  
    chmod 755 nameserver.py  
    sudo cp nameserver-daemon.sh /etc/init.d  
    sudo chmod +x nameserver-daemon.sh  
    sudo update-rc.d nameserver-daemon.sh defaults


**6. rpcserver-daemon.sh:**  
The rpcserver-daemon.sh file needs to be present in the /etc/init.d folder on the server machine. This file should be  
executed with root privileges as it creates and accesses the rpcserver.pid file from the /var/run directory.  
  
Run the following commands to give nameserver.py the appropriate access rights. Then copy the daemon shell script to the /etc/init.d folder. Then assign the daemon file with execution permission.  
  
    chmod 755 rpcserver.py  
    sudo cp rpcserver-daemon.sh /etc/init.d  
    sudo chmod +x rpcserver-daemon.sh  
    sudo update-rc.d rpcserver-daemon.sh defaults

**7. daemon-installation.sh:**  
This script needs to be run when the daemon files are copied to a new server system. This script assumes all your file  
are present in the same directory.
