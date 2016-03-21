# saved as greeting-client.py
#!/usr/bin/python

import Pyro4
import sys

name_server = Pyro4.locateNS() #Locates the name server
uri = name_server.lookup("example.mainserver") #Looks up for the registered service in the name server
main_obj = Pyro4.Proxy(uri)
print(main_obj.run_script(sys.argv[1:]))
