#!/bin/bash

sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get -y update
sudo apt-get -y install python2.7
sudo ln -s /usr/bin/python2.7 /usr/bin/python


