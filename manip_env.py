#!/usr/bin/python
import urlparse
import requests
import json
import time
import sys
from  ceph_wrapper import *
#Global variable
#haas_url = 'http://127.0.0.1:7000/'


class HaasRequest(object):
    def __init__(self, method, data):
        self.method = method
        self.data = json.dumps(data)
    def __str__(self):
        return str({"method" : str(self.method),\
                "data" : self.data})

def hookfun_pre(url, hook):
    retobj = None
    if hook:
        url, retobj = hook(url)
    return url, retobj  
    
def hookfun_post(ret, hook, retobj):
    ret_temp = None
    if hook:
        ret, ret_temp = hook(ret)
    return ret, [retobj, ret_temp]  
    
def call_haas(url, req_type, debug = None,\
        prehook = None, posthook = None):
# pre function hook

    retobj = None
    url, retobj = hookfun_pre(url, prehook)
# the actual function 
    
    ret = call_haas_inner(url, req_type, debug )
# post function hook 

    ret, retobj = hookfun_post(ret, posthook, retobj)
    return ret, retobj

def call_haas_inner(url, req_type, debug = None):
    if req_type.method == 'get':
        return requests.get(url)
    if req_type.method == "post":
        if debug:
            print req_type
            ret = requests.post(url, data=req_type.data)
            print ret
            return ret 

class HaasReturns(object):
    def __init__(self, a, b):
        self.haas_ret = a 
        self.hook_ret = b
        try:
            self.json = self.haas_ret.json()
        except Exception as e:
            self.json = False
            pass 
        
    def __str__(self):
        return str({str(self.haas_ret), str(self.hook_ret),\
                str(self.json), str(self.haas_ret.status_code)})  

#Listing nodes for Haas
def list_free_nodes(haas_url, debug = None, \
        preHooks = None, postHooks = None):
    api = 'free_nodes'
    c_api = urlparse.urljoin(haas_url, api)
    haas_req = HaasRequest('get', None)
    if debug:
        print c_api 
    free_node_list, hook_ret = call_haas(c_api, haas_req)
    return HaasReturns(free_node_list, hook_ret)   


def attach_node_haas_project(haas_url,project,node,\
        debug = None, prehooks =\
        None, posthooks = None,):
    api = '/connect_node'
    c_api = urlparse.urljoin(haas_url, 'project/' + project + api)
    ret_obj = list()
    body = {"node" : node}
    haas_req = HaasRequest('post', body)
    t_ret, t_hook_ret = call_haas(c_api, haas_req, debug)
    if debug:
        print {"url" : c_api, "node" : node}
    return t_ret, t_hook_ret

def attach_nodes_haas_proj(haas_url, project, node_list,\
        debug = None, prehooks =\
        None, posthooks = None,):
    ret_obj = list()
    for node in node_list:
        t_ret, t_hook_ret = attach_node_haas_project(haas_url, project,\
                            node, debug, prehooks, posthooks)
        ret_obj.append(HaasReturns(t_ret, t_hook_ret))       
    if debug:
        print {"node_list" : node_list}
    return ret_obj


#Function to add a node to network
def attach_node_to_project_network(haas_url, node, nic,\
        network, channel = "vlan/native",\
        debug = None, prehooks = None, post_hooks = None):
    ret_obj = list()
    api = '/node/' + node + '/nic/' + nic + '/connect_network'
    c_api = urlparse.urljoin(haas_url, api)
    print c_api
    body = {"network" : network, "channel" : channel}
    haas_req = HaasRequest('post', body)
    t_ret, t_hook_ret = call_haas(c_api, haas_req, debug)
    if debug:
        print {"url" : c_api, "node" : node, "nic" : nic}
    return t_ret, t_hook_ret

#Nic name has to be changed
def attach_to_project_network(haas_url, node_nic_list_t,\
        network, channel = "vlan/native",\
        debug = None, prehooks = None, post_hooks = None):
    ret_obj = list()
    for node, nic in node_nic_list_t:
        t_ret, t_hook_ret = attach_node_to_project_network\
                            (haas_url, node, nic, 
                             network, channel,\
                             debug, prehooks, post_hooks)
        ret_obj.append(HaasReturns(t_ret, t_hook_ret))       
    if debug:
            print { "node, nic" : node_nic_list_t}
    return ret_obj


def add_to_project(haas_url, project, node_c,\
        network, channel = "vlan/native", \
        nic = 'enp130s0f0', \
        debug = None, prehooks \
        = None, posthooks = None):
    node_tuple_list =  list()
    if debug:
        print {"node count" : str(node_c)}
    node_c = int(node_c)
    free_list = list_free_nodes(haas_url, debug).json
    if len(free_list) < node_c:
        raise Exception("count greater than available") 
    attach_ret = attach_nodes_haas_proj(haas_url,\
            project, free_list[0:node_c], debug)
    if debug:
        print attach_ret
    for ret, node in zip(attach_ret, free_list[0:node_c]):
        if ret.haas_ret.status_code  is not 404 and\
            ret.haas_ret.status_code is not 409:
            node_tuple_list.append((node, nic))
        else:
            pass 
    a_net_ret = attach_to_project_network(\
        haas_url, node_tuple_list, network,\
        channel, \
        debug)
## TODO
## We need to harden the code for Any exceptions thrown by Haas.
## these are not done here much, but in the atomics we really 
## need to, I'm not comfortable with returning free_list
    return attach_ret, a_net_ret, free_list[0:node_c]

def detach_from_project_network(haas_url, node,\
        network, nic = 'enp130s0f0', debug = None,\
        prehooks = None, post_hooks = None):
    ret_obj = list()
    api = '/node/' + node + '/nic/' + nic + '/detach_network'
    c_api = urlparse.urljoin(haas_url, api)
    body = {"network" : network}
    haas_req = HaasRequest('post', body)
    t_ret, t_hook_ret = call_haas(c_api, haas_req, debug)
    if debug:
        print {"url" : c_api, "node" : node, "nic" : nic}
    return t_ret, t_hook_ret


def detach_nodes(haas_url, project,\
        network, node_list,\
        nic = 'enp130s0f0', debug = None,\
        pre_hooks = None, post_hooks = None):
    ret_net_obj = list()
    ret_obj = list()
    for node in node_list.json:
        t_net_ret, t_net_hook_ret  = detach_from_project_network\
                        (haas_url, node, network, nic, \
                        debug, pre_hooks, post_hooks)
        ret_net_obj.append(HaasReturns(t_net_ret, t_net_hook_ret))
        time.sleep(5)
        t_ret, t_hook_ret = detach_node_from_project(haas_url, project,\
                             node, debug, pre_hooks, post_hooks)
        ret_obj.append(HaasReturns(t_ret, t_hook_ret))
    if debug:
        print {"node_list": node_list, "bla" : [a for a in ret_obj]}
    return ret_net_obj, ret_obj    

#Detaches a node from project using the HaaS API call. This usually
#receives call from detach_nodes function.
def detach_node_from_project(haas_url, project, node,\
            debug = None, pre_hooks = None,\
            post_hooks = None):
    api = '/detach_node'
    c_api = urlparse.urljoin(haas_url, 'project/' + project + api)
    ret_net_obj = list()
    body = {"node" : node}
    haas_req = HaasRequest('post', body)
    t_ret, t_hook_ret = call_haas(c_api, haas_req, debug)
    if debug:
        print {"url" : c_api, "node" : node}
    return t_ret, t_hook_ret

def query_project_nodes(haas_url, project, \
                    debug = None, pre_hooks = None,\
                    post_hooks = None):
    api = '/nodes'
    c_api = urlparse.urljoin(haas_url, '/project/' + project +  api)
    haas_req = HaasRequest('get', None)
    if debug:
        print c_api 
    free_node_list, hook_ret = call_haas(c_api, haas_req)
    return HaasReturns(free_node_list, hook_ret)   

  
def create_bigdata_env(haas_url, project, nc, network, fs_obj,\
        debug = None, pre_hooks = None,\
        post_hooks = None):
    if debug:
        print {"haas_url" : haas_url, "project" : project,\
            "node_cn" : nc, "network" : network, "fs_obj" : fs_obj}
    proj_ret = add_to_project(haas_url, project, nc, network, debug = True)
    master = proj_ret[2][0]
    print "master"
    print master
    fs_obj.clone("hadoopMaster.img".encode('utf-8'),\
            "HadoopMasterGoldenImage".encode('utf-8'),\
            master.encode("utf-8"))
# not doing clone cross context, although our wrapper allows for that
    for slave in proj_ret[2][1:]:
        fs_obj.clone("HadoopSlave.img".encode('utf-8'),\
                "HadoopSlaveGoldenImage".encode('utf-8'),\
                slave.encode("utf-8"))
    return proj_ret, fs_obj

def del_nodelist(haas_url, project, network, node_list,\
        fs_obj, debug = None,\
        pre_hooks = None, post_hooks = None):
    detached_ret = detach_nodes(haas_url, project, network,\
            node_list, debug = debug, pre_hooks = None, post_hooks = None) 
    for node in node_list.json:
        print "node to remove" + "  " + node
        fs_obj._remove(node.encode("utf-8"))



if __name__ == "__main__":
    #print   list_free_nodes('http://127.0.0.1:7000/', debug = True)
    #haas_ret =  query_project_nodes('http://127.0.0.1:7000/', 'bmi_infra', debug = True)
    #tt = list()
    #for jj in haas_ret.json:
    #    tt.append((jj, 'enp130s0f0'))
    #print tt
    if 'create' in sys.argv:
        ceph_obj = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug = True)
        cb = create_bigdata_env('http://127.0.0.1:7000/', 'bmi_infra', 2, "bmi-provision", ceph_obj, debug = True)
        ceph_obj.tear_down()
        print cb

    if 'attach' in sys.argv:
        print add_to_project('http://127.0.0.1:7000/', 'bmi_infra', 2, "bmi-provision", debug = True)
        
    node_list = query_project_nodes('http://127.0.0.1:7000/', 'bmi_infra',True)
    print node_list.json
    print "a bove is nodelsit"
    #ceph_obj =  RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug=55)
    if 'detach' in sys.argv:
        ceph_obj = RBD(rid = "henn", r_conf = "/etc/ceph/ceph.conf", pool = 'boot-disk-prototype', debug = True)
        ay = del_nodelist('http://127.0.0.1:7000/', 'bmi_infra','bmi-provision', node_list, ceph_obj, debug = True)
        ceph_obj.tear_down()
    #for kk in ay:
    #    print ay
        #time.sleep(5)
    #print  ax
    print "############################################# CLEARED ##########################"
