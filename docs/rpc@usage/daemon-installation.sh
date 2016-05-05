#!/bin/bash
#This gives appropriate permission to the nameserver python file, 
#and nameserver-daemon.sh file.
chmod 755 nameserver.py
sudo chmod +x nameserver-daemon.sh
sudo cp nameserver-daemon.sh /etc/init.d
sudo update-rc.d nameserver-daemon.sh defaults
sudo /etc/init.d/nameserver-daemon.sh start

#This gives appropriate permission to the rpcserver python file,
#and rpcserver-daemon.sh file.
chmod 755 rpcserver.py
sudo chmod +x rpcserver-daemon.sh
sudo cp rpcserver-daemon.sh /etc/init.d
sudo update-rc.d rpcserver-daemon.sh defaults
sudo /etc/init.d/rpcserver-daemon.sh start
