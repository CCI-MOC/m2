import behave 
import time # FIX: needed for inconsistency PR 120
from bmi_config import *
from subprocess import check_output, CalledProcessError, STDOUT

# Cleanup and rollback any new entries into BMI
def test_rollback(context):
    print( "      -> Performing the cleanup by rolling back...")
    while len(context.log) > 0 :
      entry = context.log.pop()
      entry_type, entry_metadata = test_get_kv_entry(entry)
      
      if entry_type == RBD_CREATE:
          test_clean_rbd_create( entry_type, entry_metadata )
          
      elif entry_type == BMI_IMPORT:
          test_clean_bmi_import( entry_type, entry_metadata )    
          
      elif entry_type == BMI_PROVISION:
          test_clean_bmi_provision( entry_type, entry_metadata )
          
      elif entry_type == BMI_SNAPSHOT:
          test_clean_bmi_snapshot( entry_type, entry_metadata )                

def test_event_store_insert(context, entry):
    try:
        context.log.append(entry)
        test_event_store_write(entry)
    except AttributeError:
        context.log = []
        context.log.append(entry)
        test_event_store_write(entry)
        
def test_event_store_write(entry):
    try:
        log_event = open("rollback.log", "a+")
        log_event.write( str(entry) + '\n' )
        log_event.flush()
        log_event.close()
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print( "Error opening to add to " + "rollback.log") 
        
def test_get_kv_entry(entry):
    for key, value in entry.iteritems():
        return key, value
    
def test_clean_rbd_create( entry_type, entry_metadata ):
    
    image_name = entry_metadata[ IMAGE_NAME ]
    
    try:
        rbd_rm_stdout = check_output('rbd rm ' + image_name, stderr=STDOUT, shell=True)
        rbd_rm_status = rbd_rm_stdout.strip()
    except CalledProcessError:
        pass # The image already exists, as it was previously created
    assert rbd_rm_status == EXPECTED_OUTPUT['rbd_rm']
    try:
        print( "      -> Checking that " + image_name + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + image_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False        
        
def test_clean_bmi_import( entry_type, entry_metadata ):
    
    image_name = entry_metadata[ IMAGE_NAME ]
    project_name = entry_metadata[ PROJECT_NAME ]
    
    bmi_remove_image_stdout = check_output('bmi rm ' + project_name + ' ' + image_name, stderr=STDOUT, shell=True)
    bmi_remove_image_status = bmi_remove_image_stdout.split('\n')
    # Pick the first (status), and split out the response
    bmi_remove_image_status = bmi_remove_image_status[0].split('-') 
    context.bmi_remove_image_status = bmi_remove_image_status[0] #.strip()
    assert context.bmi_remove_image_status == EXPECTED_OUTPUT['bmi_remove_image']
    try:
        # Ensure that the image clone actually exists in BMI and RBD
        print( "      -> Checking that " + context.import_clone + " is removed from BMI's database...")
        bmi_db_ls_stdout = check_output('bmi db ls | grep ' + context.import_clone, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False    
                    
    try:
        print( "      -> Checking that " + context.import_clone + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + context.import_clone, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False   
        
def test_clean_bmi_provision( entry_type, entry_metadata ):
    
    project_name = entry_metadata[ PROJECT_NAME ]
    node_name = entry_metadata[ NODE_NAME ]
    network_name =  entry_metadata[ NETWORK_NAME ]
    nic =  entry_metadata[ NIC ]
    
    bmi_deprovision_node_stdout = check_output('bmi dpro' + ' ' + project_name + ' ' + node_name + ' ' + network_name + ' ' + nic, stderr=STDOUT, shell=True)
    # in case in errors
    #  haas node_detach_network cisco-05 enp130s0f0 bmi-provision-dev
    context.bmi_deprovision_node_status = bmi_deprovision_node_stdout.strip()
    try:
        # Ensure that the image clone actually exists in BMI and RBD
        print( "      -> Checking that " + node_name + " is removed from BMI's database...")
        bmi_db_ls_stdout = check_output('bmi db ls | grep ' + node_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False    
                    
    try:
        print( "      -> Checking that " + context.provision_clone + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + context.provision_clone, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False
                       
    try:
        # Check the iSCSI target is not advertised anymores
        print( "      -> Checking that " + context.provision_clone + " is unadvertised by TGT...")
        tgt_status_stdout = check_output('tgt-admin -s |  grep ' + context.provision_clone + ' | grep Backing | grep store | grep path', stderr=STDOUT, shell=True)            
    except CalledProcessError:
        pass
        assert True
    else:
        assert False            
           
                               
def test_clean_bmi_snapshot( entry_type, entry_metadata ):
    
    project_name = entry_metadata[ PROJECT_NAME ]
    snapshot_name = entry_metadata[ SNAPSHOT_NAME ]
    
    bmi_snapshot_node_stdout = check_output('bmi snap rm ' + project_name + ' ' + snapshot_name, stderr=STDOUT, shell=True)
    context.bmi_snapshot_node_status = bmi_snapshot_node_stdout.strip()
    assert context.bmi_snapshot_node_status == EXPECTED_OUTPUT['bmi_snapshot_node']
    try:
        # Ensure that the image clone actually exists in BMI and RBD
        print( "      -> Checking that " + context.snapshot_clone + " is removed from BMI's database...")
        bmi_db_ls_stdout = check_output('bmi db ls | grep ' + context.snapshot_clone, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False    
                    
    try:
        print( "      -> Checking that " + context.snapshot_clone + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + context.snapshot_clone, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass 
        assert True
    else:
        assert False    
    
    
