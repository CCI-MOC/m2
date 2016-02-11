import sys
import subprocess
import threading


def create_env_wrapper(path, m_args):
	arglist = [path]
	for arg in m_args:
		print arg
		arglist.append(arg)
	print "created argslist" + str(arglist)
	proc = subprocess.Popen(arglist, stdout=subprocess.PIPE)
	return proc.communicate()
	
def parse_stdout_output(output_tuple, lookup_tuple):
	print output_tuple[0]


if __name__ == "__main__": ## use this for quick tests.. in the application we will call the functions directly.
	temp = create_env_wrapper(sys.argv[1], sys.argv[2:])
	parse_stdout_output(temp, ("blah, blah") )




