import novaclient.client as nvclient
import datetime

vms = 1 ## The only argument


OS_AUTH_URL = "https://controller-222-jeremy.staging.moc.edu:5000/v2.0"
OS_USERNAME = "admin"
OS_PASSWORD = "BRYwKZAk4Hdsj9nf"
OS_TENANT_NAME = "admin"
OS_REGION_NAME = "MOC_Test"
OS_TENANT_ID = "b4756a1e7cc04ed6926c955319e0291"
OS_PROJECT_NAME = "admin"

created_servers = []

nova = nvclient.Client("2", OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME, OS_AUTH_URL)

flavor = nova.flavors.find(name="m1.small") #Can Hardcode these
image = nova.images.find(name="ubuntu-cloud")
net = nova.networks.find(label="net 1")
nics = [{"net-id": net.id}]

start_time = datetime.datetime.now()
for i in xrange(vms):
    server = nova.servers.create("test"+str(i),flavor=flavor,image=image,nics=nics)

done = True
while not done:
    done = True
    servers = nova.servers.list()
    for server in servers:
        status = server.status
        if not status == "ACTIVE":
            done = False
            created_servers.append(server)
end_time = datetime.datetime.now()

print "Creation time"
print str(end_time - start_time)

start_time = datetime.datetime.now()
for server in created_servers:
    server.delete()

done = True
while not done:
    done = True
    servers = nova.servers.list()
    if not servers:
        done = False
end_time = datetime.datetime.now()

print "Deletion Time"
print str(end_time - start_time)