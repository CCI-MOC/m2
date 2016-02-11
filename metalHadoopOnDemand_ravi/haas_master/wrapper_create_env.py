import sys
import subprocess
import threading

def create_env_wrapper(path, m_args):
	arglist = [path]
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
	temp = create_env_wrapper(sys.argv[1], sys.argv[2:])
	parse_stdout_output(temp, ("createBigDataEnvNew.sh"))


