import behave 
from subprocess import check_output, CalledProcessError, STDOUT

@step('RBD will confirm the snapshot exists')
def rbd_confirm_snapshot_exists(context):
    for row in context.table:
        # Get Ceph clone image
        rbd_snapshot_image = context.bmi_db_name_and_ceph[ row['snapshot_name'] ]
        try:
            print( "      -> Checking that " + rbd_snapshot_image + " exists in Ceph...")
            print( "         Running: " + 'rbd ls | grep ' + rbd_snapshot_image )
            rbd_filename_check_stdout = check_output('rbd ls | grep ' + rbd_snapshot_image, stderr=STDOUT, shell=True)
        except CalledProcessError:
            # Ref: https://stackoverflow.com/questions/27222550/terminal-why-the-exit-command-of-grep-is-0-even-if-a-match-is-not-found
            assert False
        else:
            # Ref: https://stackoverflow.com/questions/16138232/is-it-a-good-practice-to-use-try-except-else-in-python
            pass
            assert True
            
        
