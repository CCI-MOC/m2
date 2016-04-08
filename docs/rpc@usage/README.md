# RPC

### Overview:  
This is the RPC server, name server and client programs to be run for the iSCSI.

### Additional packages required:  
These programs requires Pyro4 python package. The command to do so is as follows:  


    pip install Pyro4  

This package allows to build applications in which objects can talk to each other
over the network. 
  

### Folder contents:  
1. mainserver.py - This is the server program that processes the client request.  
2. nameserver.py - This is the name server program, the server registers the object 
                   with the name server and the client looks up for the object or
                   service.  
3. mainclient.py - This file is the client program that needs to be run to make a 
                   a request to the main server.
4. testclass.py  - This file is the python program that tests the MainSever class
                   in the mainserver.py file by creating objects of the class, and
                   testing the actual output of the methods against the desired output.  
  
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
  
This ip address should be reachable by name server and clients
  
**2. mainserver.py:**   
  
The mainserver.py file needs to be executed once the name server is running and listening for
the server objects. The main server is binded to a IP Address as well. This address is provided
to the Pyro server through config.HOST variable.  
  
The IP Address for the main server is to be entered in the mainserver.py file by initializing the 
 Pyro4.config.HOST in the __init__().
  
This IP Address should be reachable by name server and clients.   
  
NOTE: The name server and main server can be run on the same system as well. Still the both this 
      system will need to be configured with ip addresses the client program can reach.  
  
**3. mainclient.py:**  
  
The mainclient.py file needs to be executed with the appropriate arguments everytime a request to
the server is to be made.  
  
The example command looks as follows:  
    
    python mainclient.py provision/detach_node/create_snapshot/list_all_images arg1 arg2 .....
  
where,  
     provision/detach_node/create_snapshot/list_all_images:- These are the methods provided by the server.  
     arg1 arg2 ... :- Is the arguments that needs to be provided for a script to run.


