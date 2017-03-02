### START BMI setup
git clone -b dev http://github.com/cci-moc/ims
pushd ims

### Install BMI

sudo mkdir -p /var/log/bmi/logs /etc/bmi /opt/bmi
sudo chown -R ubuntu:ubuntu /etc/bmi /var/log/bmi /opt/bmi

wget https://gist.githubusercontent.com/sirushtim/6c28b7168f9121284364e46476af0c73/raw/a9f47dbf35a891689bfc9fe34f5fdf89f6207550/bmi_config.cfg.test
cp bmi_config.cfg.test /etc/bmi/bmiconfig.cfg
cp ims/ipxe.temp /etc/bmi/ipxe.config
cp ims/mac.temp /etc/bmi/pxelinux.cfg

sudo python setup.py develop
touch /opt/bmi/bmi.db
bmi db ls
sqlite3 /opt/bmi/bmi.db "insert into project values (0, 'bmi_infra', 'bmi_network')"

# Temporary changes to get stable CI. Need to do pull request to get this fixed.
sed -i s/"app.run(host=cfg.bind_ip, port=cfg.bind_port)"/"app.run(host=cfg.bind_ip, port=int(cfg.bind_port))"/ ims/picasso/rest.py
sed -i s/"HAAS_BMI_CHANNEL = \"vlan\/native\""/"HAAS_BMI_CHANNEL = \"null\""/ ims/common/constants.py
sed -i s/"cluster = rados.Rados(rados_id=self.rid, conffile=self.r_conf)"/"cluster = rados.Rados(conffile=self.r_conf)"/ ims/einstein/ceph.py

sudo python scripts/einstein_server &
sudo python scripts/picasso_server &

sleep 5

sudo chmod 777 /etc/tgt/conf.d/

popd

bmi db ls

### Upload Image to Ceph
wget https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
rbd import cirros-0.3.0-x86_64-disk.img --dest-pool rbd

### Interface image to BMI
bmi import bmi_infra cirros-0.3.0-x86_64-disk.img

### Fin BMI setup
