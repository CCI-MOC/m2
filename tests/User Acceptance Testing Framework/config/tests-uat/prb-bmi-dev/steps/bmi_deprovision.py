import behave 
from bmi_config import EXPECTED_OUTPUT
from subprocess import check_output, CalledProcessError, STDOUT

@step('BMI will deprovision a node')
def bmi_deprovision_node(context):
    for row in context.table:
        bmi_deprovision_node_stdout = check_output('bmi dpro' + ' ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['network_name'] + ' ' + row['NIC'], stderr=STDOUT, shell=True)
        # in case in errors
        #  haas node_detach_network cisco-05 enp130s0f0 bmi-provision-dev
        print( "         Running: " + 'bmi dpro' + ' ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['network_name'] + ' ' + row['NIC'] )
        context.bmi_deprovision_node_status = bmi_deprovision_node_stdout.strip()
        assert context.bmi_deprovision_node_status == EXPECTED_OUTPUT['bmi_deprovision_node']
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + row['node_name'] + " is removed from BMI's database...")
            print( "         Running: " + 'bmi db ls | grep ' + row['node_name'] )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + row['node_name'], stderr=STDOUT, shell=True)
            
        except CalledProcessError:
            pass
            assert True
        else:
            assert False    
                        
        try:
            print( "      -> Checking that " + context.provision_clone + " is removed from Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + context.provision_clone )          
            rbd_ls_stdout = check_output('rbd ls | grep ' + context.provision_clone, stderr=STDOUT, shell=True)
            
        except CalledProcessError:
            pass
            assert True
        else:
            assert False
                           
        try:
            # Check the iSCSI target is not advertised anymores
            print( "      -> Checking that " + context.provision_clone + " is unadvertised by TGT...")
            print( "         Running: " + 'tgt-admin -s |  grep ' + context.provision_clone + ' | grep Backing | grep store | grep path' )
            tgt_status_stdout = check_output('tgt-admin -s |  grep ' + context.provision_clone + ' | grep Backing | grep store | grep path', stderr=STDOUT, shell=True)
                        
        except CalledProcessError:
            pass
            assert True
        else:
            assert False               
                           
