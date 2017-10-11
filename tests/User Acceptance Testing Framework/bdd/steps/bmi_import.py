import behave
from bmi_db import bmi_db_name_and_ceph
from subprocess import check_output, CalledProcessError, STDOUT
from test_operation import test_event_store_insert, test_rollback
from bmi_config import BMI_IMPORT, PROJECT_NAME, IMAGE_NAME, CEPH_CLONE_NAME, EXPECTED_OUTPUT

@step('BMI will import an image') #, and populate the Name:Ceph dictionary
def bmi_import_image(context):
    for row in context.table:
        print( "         Running: " + 'bmi import ' + row['project_name'] + ' ' + row['image_name'] )
        bmi_import_image_stdout = check_output('bmi import ' + row['project_name'] + ' ' + row['image_name'], stderr=STDOUT, shell=True)
                
        context.bmi_import_image_status = bmi_import_image_stdout.strip()
        if context.bmi_import_image_status != "Success":
            print( "      Status: " + context.bmi_import_image_status )
            print( "      *** There might be snapshots associated to this image.  Please run scripts/remove-image-and-snapshots.sh IMAGE_NAME to perform a cleanup. ***")        
        assert context.bmi_import_image_status == EXPECTED_OUTPUT['bmi_import_image']
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + row['image_name'] + " exists in Ceph...")
            print( "         Running: " + 'bmi db ls | grep ' + row['image_name'] )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + row['image_name'], stderr=STDOUT, shell=True)
            
            bmi_row = bmi_db_ls_stdout.split("|")
            rbd_clone = bmi_row[4].strip()
            context.import_clone = rbd_clone
            print( "      -> Checking that " + context.import_clone + " exists in BMI's database...")
            print( "         Running: " + 'rbd ls | grep ' + rbd_clone )
            rbd_ls_stdout = check_output('rbd ls | grep ' + rbd_clone, stderr=STDOUT, shell=True)
            
        except CalledProcessError:
            assert False            
        except Exception:
            test_rollback(context)
        finally:
            test_event_store_insert(context, { BMI_IMPORT: { IMAGE_NAME : row['image_name'],
                                                             PROJECT_NAME : row['project_name'],
                                                             CEPH_CLONE_NAME : rbd_clone} })
    context.bmi_db_name_and_ceph = bmi_db_name_and_ceph()
