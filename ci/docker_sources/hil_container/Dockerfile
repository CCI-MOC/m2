FROM centos

RUN yum install -y epel-release

RUN yum -y update && yum install -y bridge-utils  gcc  httpd  ipmitool libvirt libxml2-devel  libxslt-devel  mod_wsgi net-tools python-pip python-psycopg2 python-virtinst qemu-kvm telnet vconfig virt-install

RUN yum install -y git

RUN yum install -y python-devel

RUN pip install dumb-init

RUN useradd -ms /bin/bash hil

RUN passwd -d hil

RUN passwd -d root

RUN usermod -aG wheel hil

WORKDIR /home/hil

RUN git clone https://github.com/CCI-MOC/hil.git

WORKDIR /home/hil/hil

RUN git reset --hard f88d2fc92066c1e83e428ebeeca351971f306053

RUN pip install --upgrade pip setuptools

RUN python setup.py install

COPY hil.cfg /etc/hil.cfg

COPY hil.cfg /home/hil

COPY hil.cfg /home/hil/hil

USER hil

RUN hil-admin db create

USER root

RUN chmod 666 /home/hil/hil.db

RUN chown hil:hil /home/hil/hil.db

COPY setupdb.sh setupdb.sh

RUN chmod a+x setupdb.sh

USER hil

ENV HIL_ENDPOINT=http://127.0.0.1:7000

RUN ./setupdb.sh

USER root

RUN cp hil.wsgi wsgi.py

RUN pip install gunicorn

COPY runhil.sh runhil.sh

RUN chmod a+x runhil.sh

EXPOSE 7000

user hil

CMD dumb-init /home/hil/hil/runhil.sh
