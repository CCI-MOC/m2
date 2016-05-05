#!/usr/bin/env python
import Pyro4
import json

#Reads the 'name_server_address' element from the rpc-config.json file
dict = json.loads(open('rpc-config.json').read())
name_server_address = dict['name_server_address']	
#Starting the NameServer
Pyro4.naming.startNSloop(host=name_server_address)
