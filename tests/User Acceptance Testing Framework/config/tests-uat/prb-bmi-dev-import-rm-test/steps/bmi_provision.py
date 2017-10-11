import behave 
from subprocess import check_output, CalledProcessError, STDOUT
import time
from bmi_config import BMI_PROVISION, NODE_NAME, PROJECT_NAME, NETWORK_NAME, NIC, PROVISIONING_DELAY, CEPH_CLONE_NAME, EXPECTED_OUTPUT
from test_operation import test_event_store_insert, test_rollback

@step('BMI will provision a node')
def bmi_provision_node(context):
    for row in context.table:
        #PROVISIONING_DELAY = 10
        #in case of error:
        #  haas node_detach_network cisco-05 enp130s0f0 bmi-provision-dev
        print( "         Running: " + 'bmi pro' + ' ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['image_name'] + ' ' + row['network_name'] + ' ' + row['NIC'] )
        bmi_provision_node_stdout = check_output('bmi pro' + ' ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['image_name'] + ' ' + row['network_name'] + ' ' + row['NIC'], stderr=STDOUT, shell=True)
             
        context.bmi_provision_node_status = bmi_provision_node_stdout.strip()
        time.sleep( PROVISIONING_DELAY )
        if context.bmi_import_image_status != "Success":
            print( "      Status: " + context.bmi_provision_node_status )
            print( "      *** The node might still be attached to network.  Please use HIL to run the node_detach_network command. ***")
        assert context.bmi_provision_node_status == EXPECTED_OUTPUT['bmi_provision_node']
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + row['node_name'] + " exists in BMI's database...")
            print( "         Running: " + 'bmi db ls | grep ' + row['node_name'] )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + row['node_name'], stderr=STDOUT, shell=True)
            bmi_row = bmi_db_ls_stdout.split("|")
            rbd_clone = bmi_row[4].strip()
            context.provision_clone = rbd_clone
            print( "      -> Checking that " + rbd_clone + " exists in Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + rbd_clone )
            rbd_ls_stdout = check_output('rbd ls | grep ' + rbd_clone, stderr=STDOUT, shell=True)
            # Check the iSCSI target exists
            print( "      -> Checking that " + context.provision_clone + " is advertised by TGT...")
            print( "         Running: " + 'sudo tgt-admin -s | grep ' + context.provision_clone + ' | grep Backing | grep store | grep path' )
            tgt_status_stdout = check_output('sudo tgt-admin -s | grep ' + context.provision_clone + ' | grep Backing | grep store | grep path', stderr=STDOUT, shell=True)
            # If it does not, then it will fail         
            
        except CalledProcessError:
            assert False                
        except Exception:
            test_rollback(context)    
        finally:
            test_event_store_insert(context, { BMI_PROVISION: {PROJECT_NAME : row['project_name'],
                                               NODE_NAME : row['node_name'],
                                               NETWORK_NAME : row['network_name'],
                                               NIC : row['NIC'],
                                               CEPH_CLONE_NAME : rbd_clone } })              
