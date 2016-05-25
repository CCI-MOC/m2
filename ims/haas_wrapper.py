import json
import urlparse

import requests
import constants

from exception import *


class HaasRequest(object):
    def __init__(self, method, data, auth=None):
        self.method = method
        self.data = json.dumps(data)
        self.auth = None
        if auth:
            self.auth = auth

    def __str__(self):
        return str(
            {"method": str(self.method), "data": self.data, "auth": self.auth})


def call_haas(url, req):
    if req.method == "get":
        return requests.get(url, auth=req.auth)
    if req.method == "post":
        ret = requests.post(url, data=req.data, auth=req.auth)
        return ret

def resp_parse(obj, resptype=1):
    if obj.status_code == 200 and resptype is 1:
        return {constants.STATUS_CODE_KEY: obj.status_code, constants.RETURN_VALUE_KEY: obj.json()}

    elif obj.status_code == 200 and resptype is not 1:
        return {constants.STATUS_CODE_KEY: obj.status_code}

    elif obj.status_code != 200 and obj.status_code < 400:
        return {constants.STATUS_CODE_KEY: obj.status_code}
    elif obj.status_code == 401:
        raise haas_exceptions.AuthenticationFailedException()
    elif obj.status_code == 403:
        raise haas_exceptions.AuthorizationFailedException()
    elif obj.status_code > 399:
        raise haas_exceptions.UnknownException(obj.status_code,
                                               obj.json()[constants.MESSAGE_KEY])


def list_free_nodes(haas_url, usr, passwd, debug=None):
    try:
        api = 'free_nodes'
        c_api = urlparse.urljoin(haas_url, api)
        haas_req = HaasRequest('get', None, auth=(usr, passwd))
        if debug:
            print c_api
        haas_call_ret = call_haas(c_api, haas_req)
        return resp_parse(haas_call_ret)

    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def query_project_nodes(haas_url, project, usr, passwd):
    try:
        api = '/nodes'
        c_api = urlparse.urljoin(haas_url, '/project/' + project + api)
        haas_req = HaasRequest('get', None, auth=(usr, passwd))
        haas_call_ret = call_haas(c_api, haas_req)
        return resp_parse(haas_call_ret)
    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def detach_node_from_project(haas_url, project, node, usr, passwd, debug=None):
    try:
        api = '/detach_node'
        c_api = urlparse.urljoin(haas_url, 'project/' + project + api)
        body = {"node": node}
        haas_req = HaasRequest('post', body, auth=(usr, passwd))
        t_ret = call_haas(c_api, haas_req, debug)
        if debug:
            print {"url": c_api, "node": node}
        return resp_parse(t_ret, resptype=2)
    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def attach_node_to_project_network(haas_url, node, \
                                   network, usr, passwd, channel="vlan/native", \
                                   nic='eno1'):
    try:
        api = '/node/' + node + '/nic/' + nic + '/connect_network'
        c_api = urlparse.urljoin(haas_url, api)
        body = {"network": network, "channel": channel}
        haas_req = HaasRequest('post', body, auth=(usr, passwd))
        t_ret = call_haas(c_api, haas_req)
        return resp_parse(t_ret, resptype=2)
    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def attach_node_haas_project(haas_url, project, node, usr, passwd):
    try:
        api = '/connect_node'
        c_api = urlparse.urljoin(haas_url, 'project/' + project + api)
        body = {"node": node}
        haas_req = HaasRequest('post', body, auth=(usr, passwd))
        t_ret = call_haas(c_api, haas_req)
        return resp_parse(t_ret, resptype=2)
    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def detach_node_from_project_network(haas_url, node, \
                                     network, usr, passwd, nic='eno1'):
    try:
        api = '/node/' + node + '/nic/' + nic + '/detach_network'
        c_api = urlparse.urljoin(haas_url, api)
        body = {"network": network}
        haas_req = HaasRequest('post', body, auth=(usr, passwd))
        t_ret = call_haas(c_api, haas_req)
        return resp_parse(t_ret, resptype=2)
    except requests.RequestException as e:
        raise haas_exceptions.ConnectionException()


def check_auth(haas_url, usr, passwd, project):
    api = '/nodes'
    c_api = urlparse.urljoin(haas_url, '/project/' + project + api)
    haas_req = HaasRequest('get', None, auth=(usr, passwd))
    ret = call_haas(c_api, haas_req)
    code = ret.status_code
    if code == 401:
        raise haas_exceptions.AuthenticationFailedException()
    elif code == 403:
        raise haas_exceptions.AuthorizationFailedException()
    elif not code == 200:
        raise haas_exceptions.UnknownException(code, ret.content)
