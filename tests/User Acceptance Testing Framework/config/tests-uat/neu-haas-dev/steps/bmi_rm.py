import behave
from bmi_config import EXPECTED_OUTPUT
from subprocess import check_output, CalledProcessError, STDOUT

@step('BMI will remove an image') # (Name), populate the Name:Ceph dictionary and check its removal')
def bmi_remove_image(context):
    for row in context.table:
        print( "         Running: " + 'bmi rm ' + row['project_name'] + ' ' + row['image_name'] )
        bmi_remove_image_stdout = check_output('bmi rm ' + row['project_name'] + ' ' + row['image_name'], stderr=STDOUT, shell=True)
        bmi_remove_image_status = bmi_remove_image_stdout.split('\n')
        # Pick the first (status), and split out the response
        bmi_remove_image_status = bmi_remove_image_status[0].split('-') 
        context.bmi_remove_image_status = bmi_remove_image_status[0] #.strip()
        assert context.bmi_remove_image_status == EXPECTED_OUTPUT['bmi_remove_image']
        try:
            # Ensure that the image clone actually exists in BMI and RBD
            print( "      -> Checking that " + context.import_clone + " is removed from BMI's database...")
            print( "         Running: " + 'bmi db ls | grep ' + context.import_clone )
            bmi_db_ls_stdout = check_output('bmi db ls | grep ' + context.import_clone, stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass
            assert True
        else:
            assert False    
                        
        try:
            print( "      -> Checking that " + context.import_clone + " is removed from Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + context.import_clone )          
            rbd_ls_stdout = check_output('rbd ls | grep ' + context.import_clone, stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass
            assert True
        else:
            assert False   
    
    
