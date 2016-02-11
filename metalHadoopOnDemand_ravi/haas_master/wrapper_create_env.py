#! /bin/python
import sys
import subprocess
import threading

def call_shellscript(path, m_args, ssh_cmdline):
	arglist = ssh_cmdline
	arglist.append(path)
	print arglist
        print "the above is the cmdline that will run on the current machine"
	for arg in m_args:
		print arg
		arglist.append(arg)
	print "created argslist" + str(arglist)
	proc = subprocess.Popen(arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return proc.communicate()
	
def parser_for_create(script_output):
	master_node = None
	slave_nodes = list() 
	bigdatatime = str()
	script_output = script_output[0].splitlines()
	for line in script_output:
		if "MASTER:" in line:
			master_node = line.split(":")[1]
		elif "SLAVE:" in line:
			slave_nodes.append(line.split(":")[1])
		elif "BIGDATATIME:" in line:
			bigdatatime = line.split("BIGDATATIME:")[1]
		else:
			pass
	return master_node, slave_nodes, bigdatatime

def parser_for_cleaning_nodes(script_output):
	script_output = script_output[0]
	for line in script_output:
		if "CLEANEDEVERYTHING" in line:
			return True

global parser_dict
parser_dict = {("createBigDataEnvNew.sh") : parser_for_create,
		("cleanBigDataEnvNew")    : parser_for_cleaning_nodes, 
		}

def parse_stdout_output(output_tuple, lookup_tuple): #just a lookup parser
	global parser_dict
	output = parser_dict[lookup_tuple](output_tuple)
	print output

if __name__ == "__main__": ## use this for quick tests.. in the application we will call the functions directly.
        hardcoded_ssh = ["ssh", "-A", "psurana@129.10.3.48", "-C"]
	temp = call_shellscript(sys.argv[1], sys.argv[2:],hardcoded_ssh)
	parse_stdout_output(temp, ("createBigDataEnvNew.sh"))

