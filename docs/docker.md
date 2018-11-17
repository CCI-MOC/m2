# Docker for Dev

## Prerequisites

* Docker

## Creating Containers

### Ceph

To Run Ceph Container execute
```
docker pull ceph/demo
docker run -d -v ceph:/etc/ceph -e MON_IP=172.17.0.2 -e CEPH_PUBLIC_NETWORK=172.17.0.0/24 --name ceph -h ceph ceph/demo
```

Do a ``` docker ps ``` and check if ceph container is running and to check if ceph is running probably do ``` docker exec ceph ceph -s ```
and if the output contains HEALTH_OK then all is good.

### HIL

To build HIL image, first cd to the project root folder then execute
```
docker build -t hil -f ./Dockerfile_hil
```

After Successful build of image execute
```
docker run -d --name hil -h hil hil
```
Then run ``` docker ps ``` to check if container is running

### BMI

Similar to HIL, first cd to the project root folder then execute
```
docker build -t bmi .
```

After successful build of image execute
```
docker run -d -v ceph:/etc/ceph --link hil:hil --name bmi -h bmi bmi
```
Then run ``` docker ps ``` to check if container is running

Hopefully you have a successful deployment of BMI running on your system in containers!!

## Running

Like after system reboot it is advised to start containers in the following order using ``` docker start <name> ```
* ceph
* hil
* bmi
To get the correct ips.

## Getting in the container

To get in the bmi container run the command ``` docker exec -it bmi bash ```, You can configure the container any way you want. BMI is already
installed as develop with production configuration. The src files are in /home/bmi.

## Post Config Stuff for BMI

Even though bmi is technically ready to run you will probably need to do some more stuff to run it properly.
* Create new image using ``` rbd create --image-format 2 --size 10 bmi_test ```, this will create a 10 MB blank image called bmi_test in
ceph.
* import the created image using ``` bmi import bmi_infra bmi_test ```
* Change HIL_BMI_CHANNEL to null in ims/common/constants.py (Temporary)

This should allow you to run test cases.

## HIL side stuff
* network = bmi_provision
* node = bmi_node
* nic = bmi_nic
* port = bmi_port
* switch = bmi_switch
