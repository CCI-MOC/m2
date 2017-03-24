FROM ubuntu

# RUN echo "deb http://ceph.com/packages/ceph-extras/debian $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/ceph-extras.list
RUN apt-get -y update && apt-get install -y tgt-rbd ceph-common python python-dev python-setuptools build-essential python-pip sudo sqlite3

# Dev doesnt need dnsmasq for now, will require for prod
# RUN apt-get install -y dnsmasq

# TODO update dnsmasq.conf and other stuff when updating for prod

RUN pip install dumb-init

RUN useradd -ms /bin/bash bmi
RUN passwd -d bmi
RUN usermod -aG sudo bmi
COPY ims/ /home/bmi/ims/
COPY tests/ /home/bmi/tests/
COPY scripts/ /home/bmi/scripts/
COPY setup.py /home/bmi/setup.py

WORKDIR /home/bmi
RUN python setup.py install

RUN mkdir /etc/bmi/
RUN mkdir /var/log/bmi/
RUN mkdir /var/lib/tftpboot/
RUN mkdir /var/lib/tftpboot/pxelinux.cfg/
RUN mkdir /var/lib/bmi/

COPY docker/bmi_config.cfg /etc/bmi/bmiconfig.cfg

RUN chown bmi:bmi /var/log/bmi/
RUN chown bmi:bmi /var/lib/tftpboot/
RUN chown bmi:bmi /var/lib/tftpboot/pxelinux.cfg/
RUN chown bmi:bmi /var/lib/bmi/

COPY docker/runbmi.sh ./runbmi.sh
RUN chmod a+x runbmi.sh

ENV HAAS_USERNAME=admin
ENV HAAS_PASSWORD=admin

VOLUME /etc/ceph

USER bmi
RUN bmi db ls
RUN sqlite3 /var/lib/bmi/bmi.db "insert into project values(1,'bmi_infra','bmi_provision')"


CMD dumb-init /home/bmi/runbmi.sh
