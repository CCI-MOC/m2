# This File is to create the image for BMI environment.
# It will install all dependencies and create the required folder structure
# The CI Tool will just create a new image based of this and run tests

# Using ubuntu as base
FROM ubuntu

# Install all dependencies except dnsmasq
RUN apt-get -y update && apt-get install -y tgt-rbd ceph-common python python-dev python-setuptools build-essential python-pip sudo sqlite3 git

# Install test stuff
RUN pip install dumb-init pytest pytest-random-order coverage==4.3 pytest-cov coveralls

# Create user and remove password for root
RUN useradd -ms /bin/bash bmi
RUN passwd -d bmi
RUN passwd -d root
RUN usermod -aG sudo bmi

# Create required folders
RUN mkdir /etc/bmi/
RUN mkdir /var/log/bmi/
RUN mkdir /var/lib/tftpboot/
RUN mkdir /var/lib/tftpboot/pxelinux.cfg/
RUN mkdir /var/lib/bmi/

# Add config file
COPY docker/bmi_config.cfg /etc/bmi/bmiconfig.cfg
ENV BMI_CONFIG=/etc/bmi/bmiconfig.cfg

# Set Permissions
RUN chown bmi:bmi /etc/tgt/conf.d/
RUN chown bmi:bmi /var/log/bmi/
RUN chown bmi:bmi /var/lib/tftpboot/
RUN chown bmi:bmi /var/lib/tftpboot/pxelinux.cfg/
RUN chown bmi:bmi /var/lib/bmi/

# Add the BMI execute script
COPY docker/runbmi.sh /home/bmi/runbmi.sh
RUN chmod a+x /home/bmi/runbmi.sh

# Set Environment variables
# We can easily override these when launching the container
ENV HIL_USERNAME=admin
ENV HIL_PASSWORD=admin

# Expose as volume to get keyring and ceph config
VOLUME /etc/ceph
