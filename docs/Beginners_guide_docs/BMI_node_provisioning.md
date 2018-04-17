The execution involves the following steps. Please note all the steps below are to be executed as root user.

1. Start the Picasso (frontend) server as follows:

```
	>> screen 
	>> picasso_server

	If successful it should show something like below
	* Running on http://10.10.10.1:1513/ (Press CTRL+C to quit)

```
2. Start the Einstein (backend) server as follows:
```
	>> screen
	>> einstein_server

	If successful it should show something like below
	Broadcast server running on 0.0.0.0:9091
	NS running on 10.10.10.1:9893 (10.10.10.1)
	Warning: HMAC key not set. Anyone can connect to this server!
	URI = PYRO:Pyro.NameServer@10.10.10.1:9893
```

Note : Few errors one could face at this phase
 		1. Address already in use : socket error -> This is a well known socket error, killing the process and restarting should resolve it.

```
 		 ps aux | grep picasso/einstein
 		 kill -9 <process number>
```
 2. Permission denied : Probably not executing it as root user.


3. bmi --help will list down all the bmi commands

4. To provision a node the command is as follows

```
		Usage: bmi pro [OPTIONS] PROJECT NODE IMG NETWORK NIC

		EG: bmi pro vj dell-8 centos_67_e1 bmi-provision-vj em1
```


Possible errors one may face:
------------------------------

Enable debug and verbose in bmi_config.cfg. The logs can be found under path "var/log/bmi/"

1. Connection reject :
	Better to try again.

2. Got status code 409 from HIL with message :
	Node not in project : The node assigned to be provisioned has been freed and is no longer part of the (your) project. Need to reacquire it. The link https://github.com/CCI-MOC/kumo-leasing/blob/master/instructions.md has all the necessary information for the same.

3. Couldn't connect to HIL : 
	Check logs for reason for HIL connection exception. Test HIL_ENDPOINT connection through ping and curl. If thats fine check further from logs to see where the exception occurred. Some common mistakes include additional or wrong quotes in url in bmi_config.cfg, which result in request.gets error.

