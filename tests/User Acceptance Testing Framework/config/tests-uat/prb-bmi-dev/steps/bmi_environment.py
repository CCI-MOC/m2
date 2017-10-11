import behave 
import subprocess
from bmi_config import LOG_FILE_MINIMUM_THRESHOLD_OF_LINE_NUMBER_WRITES

# As described by Apoorve in terms of requirements for 0.5 in:
#
#   https://github.com/CCI-MOC/ims/issues/120
#

@step('the operating system')
def linux_distro_check(context):
    for row in context.table:
        print( "         Running: " + 'cat /etc/redhat-release' )
        linux_distro_stdout = subprocess.check_output('cat /etc/redhat-release', stderr=subprocess.STDOUT, shell=True)
        context.linux_distro = linux_distro_stdout.strip()
        assert context.linux_distro == row['linux_distribution'].strip()

@step('Ceph (RBD) version')
def ceph_version_check(context):
    for row in context.table:
        # Running RBD since running ceph in a virtualenv causes errors
        print( "         Running: " + 'rbd --version | cut -f3 -d\' \'' )
        ceph_version_stdout = subprocess.check_output('rbd --version | cut -f3 -d\' \'', stderr=subprocess.STDOUT, shell=True)
        context.ceph_version = ceph_version_stdout.strip()
        assert int(context.ceph_version.replace('.','')) >= int(row['ceph_version'].strip().replace('.',''))
    
@step('dnsmasq version')
def dnsmasq_version_check(context):
    for row in context.table:
        print( "         Running: " + 'dnsmasq -version | head -n1 | cut -f3  -d\' \'' )
        dnsmasq_version_stdout = subprocess.check_output('dnsmasq -version | head -n1 | cut -f3  -d\' \'', stderr=subprocess.STDOUT, shell=True)
        context.dnsmasq_version = dnsmasq_version_stdout.strip()
        assert int(context.dnsmasq_version.replace('.','')) >= int(row['dnsmasq_version'].strip().replace('.',''))

@step('Linux target framework (tgt)')
def tgt_version_check(context):
    for row in context.table:    
        print( "         Running: " + 'tgtadm --version | head -n1 | cut -f1  -d\' \'' )
        tgt_version_stdout = subprocess.check_output('tgtadm --version | head -n1 | cut -f1  -d\' \'', stderr=subprocess.STDOUT, shell=True)
        context.tgt_version = tgt_version_stdout.strip()
        assert int(context.tgt_version.replace('.','')) >= int(row['tgt_version'].strip().replace('.',''))
    
@step('BMI log line-count will be measured at the beginning')
def bmi_log_line_count_at_start(context):
    print( "         Running: " + 'cat $BMI_CONFIG | grep log | cut -f3 -d\' \' | tail -n 1' )
    log_file_stdout = subprocess.check_output('cat $BMI_CONFIG | grep log | cut -f3 -d\' \' | tail -n 1', stderr=subprocess.STDOUT, shell=True)
    log_file_name = log_file_stdout.strip() + "ims.log"
    print( "         Running: " + 'wc -l ' + log_file_name + ' | cut -f1 -d\' \'' )
    log_file_size_stdout = subprocess.check_output('wc -l ' + log_file_name + ' | cut -f1 -d\' \'', stderr=subprocess.STDOUT, shell=True)
    context.log_file_start_size = int( log_file_size_stdout.strip() )

@step('BMI log line-count will be measured at the end')
def bmi_log_line_count_at_end(context):
    print( "         Running: " + 'cat $BMI_CONFIG | grep log | cut -f3 -d\' \' | tail -n 1' )
    log_file_stdout = subprocess.check_output('cat $BMI_CONFIG | grep log | cut -f3 -d\' \' | tail -n 1', stderr=subprocess.STDOUT, shell=True)
    log_file_name = log_file_stdout.strip() + "ims.log"
    print( "         Running: " + 'wc -l ' + log_file_name + ' | cut -f1 -d\' \'' )
    log_file_size_stdout = subprocess.check_output('wc -l ' + log_file_name + ' | cut -f1 -d\' \'', stderr=subprocess.STDOUT, shell=True)
    context.log_file_end_size = int( log_file_size_stdout.strip() )
    assert (context.log_file_end_size - context.log_file_start_size) >= LOG_FILE_MINIMUM_THRESHOLD_OF_LINE_NUMBER_WRITES
    
    
