#!/usr/bin/python

import behave 
import time # FIX: needed for inconsistency PR 120
from bmi_config import * # FIX: needed for inconsistency PR 120
from subprocess import check_output, CalledProcessError, STDOUT
import ast

rollback_log = []

def main():
    
    load_rollback_log()
    perform_rollback()

def load_rollback_log():
    
    global rollback_log
    
    try:
        with open("rollback.log",'r') as f:
            while True:
                line_entry = f.readline()
                if not line_entry: break
                line_entry = line_entry.rstrip('\n')
                rollback_log.append( line_entry )
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        print( "Error opening " + "rollback.log" )


# Cleanup and rollback any new entries into BMI
def perform_rollback():
        
    global rollback_log
    
    print( "      -> Performing the cleanup by rolling back...")
    while len( rollback_log ) > 0 :
      entry = ast.literal_eval( rollback_log.pop() )
      print(entry)
      entry_type, entry_metadata = test_get_kv_entry(entry)
      
      if entry_type == RBD_CREATE:
          test_clean_rbd_create( entry_type, entry_metadata )
          
      elif entry_type == BMI_IMPORT:
          test_clean_bmi_import( entry_type, entry_metadata )    
          
      elif entry_type == BMI_PROVISION:
          test_clean_bmi_provision( entry_type, entry_metadata )
          
      elif entry_type == BMI_SNAPSHOT:
          test_clean_bmi_snapshot( entry_type, entry_metadata )                

            
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
    ceph_clone_name =  entry_metadata[ CEPH_CLONE_NAME ]
    
    bmi_remove_image_stdout = check_output('bmi rm ' + project_name + ' ' + image_name, stderr=STDOUT, shell=True)
    bmi_import_image_status = bmi_remove_image_stdout.split('\n')
    # Pick the first (status), and split out the response
    bmi_import_image_status = bmi_import_image_status[0].split('-') 
    bmi_import_image_status = bmi_import_image_status[0] #.strip()
    try:
        # Ensure that the image clone actually exists in BMI and RBD
        print( "      -> Checking that " + ceph_clone_name + " is removed from BMI's database...")
        bmi_db_ls_stdout = check_output('bmi db ls | grep ' + ceph_clone_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False    
                    
    try:
        print( "      -> Checking that " + ceph_clone_name + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + ceph_clone_name, stderr=STDOUT, shell=True)
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
    ceph_clone_name =  entry_metadata[ CEPH_CLONE_NAME ]
    
    bmi_deprovision_node_stdout = check_output('bmi dpro' + ' ' + project_name + ' ' + node_name + ' ' + network_name + ' ' + nic, stderr=STDOUT, shell=True)
    # in case in errors
    #  haas node_detach_network cisco-05 enp130s0f0 bmi-provision-dev
    bmi_deprovision_node_status = bmi_deprovision_node_stdout.strip()
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
        print( "      -> Checking that " + ceph_clone_name + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + ceph_clone_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False
                       
    try:
        # Check the iSCSI target is not advertised anymores
        print( "      -> Checking that " + ceph_clone_name + " is unadvertised by TGT...")
        tgt_status_stdout = check_output('tgt-admin -s |  grep ' + ceph_clone_name + ' | grep Backing | grep store | grep path', stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False            
           
                               
def test_clean_bmi_snapshot( entry_type, entry_metadata ):
    
    project_name = entry_metadata[ PROJECT_NAME ]
    snapshot_name = entry_metadata[ SNAPSHOT_NAME ]
    ceph_clone_name =  entry_metadata[ CEPH_CLONE_NAME ]
    
    bmi_snapshot_node_stdout = check_output('bmi snap rm ' + project_name + ' ' + snapshot_name, stderr=STDOUT, shell=True)
    bmi_snapshot_node_status = bmi_snapshot_node_stdout.strip()
    try:
        # Ensure that the image clone actually exists in BMI and RBD
        print( "      -> Checking that " + ceph_clone_name + " is removed from BMI's database...")
        bmi_db_ls_stdout = check_output('bmi db ls | grep ' + ceph_clone_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass
        assert True
    else:
        assert False    
                    
    try:
        print( "      -> Checking that " + ceph_clone_name + " is removed from Ceph...")          
        rbd_ls_stdout = check_output('rbd ls | grep ' + ceph_clone_name, stderr=STDOUT, shell=True)
    except CalledProcessError:
        pass 
        assert True
    else:
        assert False    
    
# Insures that the starting function is the main function

if __name__ == "__main__":
    main()


    
