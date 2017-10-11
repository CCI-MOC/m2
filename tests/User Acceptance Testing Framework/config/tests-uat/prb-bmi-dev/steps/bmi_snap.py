import behave
from bmi_db import bmi_db_name_and_ceph 
from subprocess import check_output, CalledProcessError, STDOUT
from test_operation import test_event_store_insert, test_rollback
from bmi_config import BMI_SNAPSHOT, PROJECT_NAME, SNAPSHOT_NAME, CEPH_CLONE_NAME, EXPECTED_OUTPUT

@step('BMI will create a snapshot of a node') 
def bmi_snapshot_node_create(context):
    # This snapshot will appear under Name in the column and create a Ceph
    for row in context.table:
        print( "         Running: " + 'bmi snap create ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['snapshot_name'] )
        bmi_snapshot_node_stdout = check_output('bmi snap create ' + row['project_name'] + ' ' + row['node_name'] + ' ' + row['snapshot_name'], stderr=STDOUT, shell=True)

        context.bmi_snapshot_node_status = bmi_snapshot_node_stdout.strip()
        if context.bmi_snapshot_node_status != "Success":
            print( "      Status: " + context.bmi_snapshot_node_status )
            print( "      *** There might be snapshots associated to this image.  Please run scripts/remove-image-and-snapshots.sh IMAGE_NAME to perform a cleanup. ***")
        assert context.bmi_snapshot_node_status == "Success"
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + row['snapshot_name'] + " exists in BMI's database...")
            print( "         Running: " + 'bmi db ls | grep ' + row['snapshot_name'] )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + row['snapshot_name'], stderr=STDOUT, shell=True)
            bmi_row = bmi_db_ls_stdout.split("|")
            rbd_clone = bmi_row[4].strip()
            context.snapshot_clone = rbd_clone
            print( "      -> Checking that " + rbd_clone + " exists in Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + rbd_clone ) 
            rbd_ls_stdout = check_output('rbd ls | grep ' + rbd_clone, stderr=STDOUT, shell=True)
            
        except CalledProcessError:
            assert False    
        except Exception:
            test_rollback(context)    
        finally:
            test_event_store_insert(context, { BMI_SNAPSHOT: {PROJECT_NAME : row['project_name'],
                                               SNAPSHOT_NAME : row['snapshot_name'],
                                               CEPH_CLONE_NAME : rbd_clone } })               
    context.bmi_db_name_and_ceph = bmi_db_name_and_ceph()


@step('BMI will remove a snapshot') 
def bmi_snapshot_node_remove(context):
    for row in context.table:
        print( "         Running: " + 'bmi snap rm ' + row['project_name'] + ' ' + row['snapshot_name'] )
        bmi_snapshot_node_stdout = check_output('bmi snap rm ' + row['project_name'] + ' ' + row['snapshot_name'], stderr=STDOUT, shell=True)
        context.bmi_snapshot_node_status = bmi_snapshot_node_stdout.strip()
        assert context.bmi_snapshot_node_status == EXPECTED_OUTPUT['bmi_snapshot_node']
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + context.snapshot_clone + " is removed from BMI's database...")
            print( "         Running: " + 'bmi db ls | grep ' + context.snapshot_clone )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + context.snapshot_clone, stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass
            assert True
        else:
            assert False    
                        
        try:
            print( "      -> Checking that " + context.snapshot_clone + " is removed from Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + context.snapshot_clone )          
            rbd_ls_stdout = check_output('rbd ls | grep ' + context.snapshot_clone, stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass 
            assert True
        else:
            assert False    
        
