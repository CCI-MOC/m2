set -x

### START BMI setup

TOP_DIR=$(cd $(dirname "$0") && pwd)

# Move to main ims directory for install from script location
pushd $TOP_DIR/../../

### Install BMI

user=`whoami`
sudo mkdir -p /var/log/bmi/logs /etc/bmi /opt/bmi
sudo chown -R $user:$user /etc/bmi /var/log/bmi /opt/bmi
sudo chmod 775 /etc/bmi /var/log/bmi /opt/bmi

### Copy config/template files
cp bmi_config.cfg.test /etc/bmi/bmiconfig.cfg
cp ims/ipxe.temp /etc/bmi/ipxe.config
cp ims/mac.temp /etc/bmi/pxelinux.cfg

virtualenv .bmi_venv
source .bmi_venv/bin/activate
pip install python-cephlibs
python setup.py develop

touch /opt/bmi/bmi.db

export HIL_USERNAME=hil
export HIL_PASSWORD=secret

bmi db ls
sqlite3 /opt/bmi/bmi.db "insert into project values (0, 'bmi_infra', 'bmi_network')"

# Temporary changes to get stable CI. Need to do pull request to get this fixed.
sed -i s/"HIL_BMI_CHANNEL = \"vlan\/native\""/"HIL_BMI_CHANNEL = \"null\""/ ims/common/constants.py

python scripts/einstein_server &
python scripts/picasso_server &

sleep 5

# This is weird
sudo chmod 777 /etc/tgt/conf.d/

popd

bmi db ls

### Upload Image to Ceph
wget https://launchpad.net/cirros/trunk/0.3.0/+download/cirros-0.3.0-x86_64-disk.img
rbd import cirros-0.3.0-x86_64-disk.img --dest-pool rbd

### Interface image to BMI
bmi import bmi_infra cirros-0.3.0-x86_64-disk.img

cat >bmi_userrc.sh <<EOL
export HIL_USERNAME=hil
export HIL_PASSWORD=secret
EOL

### Fin BMI setup
