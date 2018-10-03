# This File is to create the image for BMI environment.
# It will install all dependencies and create the required folder structure
# The CI Tool will just create a new image based of this and run tests

# Using ubuntu as base
FROM centos

# Install all dependencies except dnsmasq
RUN yum install -y epel-release
RUN rpm --import 'https://download.ceph.com/keys/release.asc'
COPY yum.repo /etc/yum.repos.d/ceph.repo
RUN yum -y update && yum install -y ceph-common-0.94.9 librbd1-devel-0.94.9 librados2-devel-0.94.9 python python-setuptools python-pip sudo sqlite cpan perl-Config-General libxslt-devel git make gcc

# Install test stuff
RUN pip install dumb-init pytest pytest-random-order coverage==4.3 pytest-cov coveralls

RUN git clone https://github.com/fujita/tgt
WORKDIR tgt/
RUN git reset --hard 3c8c9e96b82d87a334b1d340fa29218b7b94f26d
RUN sudo make CEPH_RBD=1 clean
RUN sudo make CEPH_RBD=1
RUN sudo make CEPH_RBD=1 install

WORKDIR ../
# Create user and remove password for root
RUN useradd -ms /bin/bash bmi
RUN passwd -d bmi
RUN passwd -d root
RUN usermod -aG wheel bmi

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
ENV HIL_USERNAME=admin
ENV HIL_PASSWORD=admin

# Expose as volume to get keyring and ceph config
VOLUME /etc/ceph
