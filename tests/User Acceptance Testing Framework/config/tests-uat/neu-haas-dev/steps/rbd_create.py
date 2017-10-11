import behave 
import time # FIX: needed for inconsistency PR 120
from bmi_config import RBD_CREATE, IMAGE_NAME, PROVISIONING_DELAY
from subprocess import check_output, CalledProcessError, STDOUT
from test_operation import test_event_store_insert, test_rollback

@step('RBD will create an image')
def rbd_create_image(context):
    for row in context.table:
        try:
            print( "      -> Checking that no pre-existing " + row['image_name'] + " is present in Ceph, before creating it...")
            print( "         Running: " + 'rbd ls | grep ' + row['image_name'] )
            rbd_filename_check_stdout = check_output('rbd ls | grep ' + row['image_name'], stderr=STDOUT, shell=True)
            if rbd_filename_check_stdout.strip() != "":
                print("      *** An image of this name already exists! ***")
                assert rbd_filename_check_stdout.strip() == ""
        except CalledProcessError:
            pass # The image already exists, as it was previously created
        
        try:
            print( "      -> Creating the " + row['image_name'] + " image in Ceph...")
            print( "         Running: " + 'rbd create ' + row['image_name'] + ' --size 1 --image-format 2' )
            rbd_create_stdout = check_output('rbd create ' + row['image_name'] + ' --size 1 --image-format 2', stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass # The image already exists, as it was previously created
        except Exception:
            test_rollback(context)
        finally:
            test_event_store_insert(context, { RBD_CREATE: { IMAGE_NAME : row['image_name'] } } )
        print( "      -> Checking that " + row['image_name'] + " exists in Ceph...")
        print( "         Running: " + 'rbd ls | grep ' + row['image_name'] )
        rbd_filename_check_stdout = check_output('rbd ls | grep ' + row['image_name'], stderr=STDOUT, shell=True)
        context.rbd_filename_check = rbd_filename_check_stdout.strip()
        
        time.sleep( PROVISIONING_DELAY ) # FIX: needed for inconsistency PR 120
        assert context.rbd_filename_check == row['image_name']

