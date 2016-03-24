#! env python
import urlparse
import requests

#Global variable
haas_url="http://127.0.0.1:7000/"


def preHooks():
	print "Checking for free nodes in the list"
	

#Listing nodes for Haas
def add_nodes_to_project(preHooks,postHooks):
	global haas_url
	if preHooks == "None":
		free_node_list =  urlparse.urljoin(haas_url,'free_nodes')
		free_node_list = requests.get(free_node_list)
		print free_node_list.json()
	else:
		preHooks()

if __name__ == "__main__":
	haas_list_nodes(preHooks,"None")
	haas_list_nodes("None", "None")
