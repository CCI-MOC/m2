#! env python
import urlparse
import requests
import json
#Global variable
#haas_url = 'http://127.0.0.1:7000/'


class HaasRequest(object):
    def __init__(self, method, data):
        self.method = method
        self.data = json.dumps(data)
    def __str__(self):
        return str({"method" : str(self.method), "data" : self.data})

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
    
def call_haas(url, req_type, debug = None, prehook = None, posthook = None):
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
        return requests.post(url, data=req_type.data)
        

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
        return str({str(self.haas_ret), str(self.hook_ret), str(self.json), str(self.haas_ret.status_code)})  

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



def attach_nodes_haas_proj(haas_url, project, node_list, debug = None, prehooks =\
        None, posthooks = None,):
    api = '/connect_node'

    c_api = urlparse.urljoin(haas_url, 'project/' + project + api)
    ret_obj = list()
    for node in node_list:
        body = {"node" : node}
        haas_req = HaasRequest('post', body)
        t_ret, t_hook_ret = call_haas(c_api, haas_req, debug)
        ret_obj.append(HaasReturns(t_ret, t_hook_ret))       
    if debug:
        print {"url" : c_api, "node_list" : node_list}

    return ret_obj


def attach_to_project_network(haas_url, project, node_list,\
        debug = None, prehooks = None, post_hooks = None):
    pass

def add_to_project(haas_url, project, node_c, debug = None, prehooks \
        = None, posthooks = None):
    if debug:
        print "node count : " + str(node_c)
    node_c = int(node_c)
    free_list = list_free_nodes(haas_url, debug).json
    if len(free_list) < node_c:
        raise Exception("count greater than available") 
    return attach_nodes_haas_proj(haas_url, project, free_list[0:node_c], debug) 

if __name__ == "__main__":
    haas_ret =  add_to_project('http://127.0.0.1:7000/', 'bmi_infra', 2, debug = True)
    for ret in haas_ret:
        print ret
