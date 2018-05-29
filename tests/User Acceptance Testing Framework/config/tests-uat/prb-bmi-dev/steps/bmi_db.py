import behave 
from subprocess import check_output, CalledProcessError, STDOUT

# Get the Name and Ceph columns from "bmi db ls" as a Name:Ceph dictionary
def bmi_db_name_and_ceph():
    bmi_db_name_ceph_cols_stdout = check_output('bmi db ls | cut -f3,5 -d\'|\' | tail -n +4 | head -n -1', stderr=STDOUT, shell=True)
    bmi_db_name_ceph_cols = bmi_db_name_ceph_cols_stdout.split('\n')
    bmi_db_name_ceph = {}
    for row in range(0,len(bmi_db_name_ceph_cols)-1):
        name_ceph = bmi_db_name_ceph_cols[row].split('|')
        name = name_ceph[0].strip()
        ceph = name_ceph[1].strip()
        bmi_db_name_ceph[ name ] = ceph
    return(bmi_db_name_ceph)
        
