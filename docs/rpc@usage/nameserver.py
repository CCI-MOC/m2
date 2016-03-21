import Pyro4
import json

#Loads the variable dict with the contents of config.json.
dict = json.loads(open('config.json').read())
server_details = dict['server-details'] #The server ip addresses.
#The address on which the NameServer is binded on.
ip_address = server_details['name-server-address']
#Starting the NameServer
Pyro4.naming.startNSloop(host=ip_address)
