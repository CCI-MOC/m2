import behave 
from bmi_config import EXPECTED_OUTPUT
from subprocess import check_output, CalledProcessError, STDOUT

@step('RBD will confirm the removed image\'s clone')
def rbd_confirm_removed_image(context):
    for row in context.table:
        # Get Ceph clone image
        rbd_clone_image = context.bmi_db_name_and_ceph[ row['image_name'] ]
        try:
            print( "      -> Checking that " + rbd_clone_image + " is removed from Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + rbd_clone_image )
            rbd_filename_check_stdout = check_output('rbd ls | grep ' + rbd_clone_image, stderr=STDOUT, shell=True)
        except CalledProcessError:
            # Ref: https://stackoverflow.com/questions/27222550/terminal-why-the-exit-command-of-grep-is-0-even-if-a-match-is-not-found
            pass # Since the filename is not present and grep will return an error code of 1 ($?)
            assert True
        else:
            # Ref: https://stackoverflow.com/questions/16138232/is-it-a-good-practice-to-use-try-except-else-in-python
            assert False
        

@step('RBD will remove the created image')
def rbd_rm_image(context):
    for row in context.table:
        try:
            print( "         Running: " + 'rbd rm ' + row['image_name'] )
            rbd_rm_stdout = check_output('rbd rm ' + row['image_name'], stderr=STDOUT, shell=True)
            rbd_rm_status = rbd_rm_stdout.strip()
        except CalledProcessError:
            pass # The image already exists, as it was previously created
        assert rbd_rm_status == EXPECTED_OUTPUT['rbd_rm']
        try:
            print( "      -> Checking that " + row['image_name'] + " is removed from Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + 'image_name' )          
            rbd_ls_stdout = check_output('rbd ls | grep ' + 'image_name', stderr=STDOUT, shell=True)
        except CalledProcessError:
            pass
            assert True
        else:
            assert False   
        
        
