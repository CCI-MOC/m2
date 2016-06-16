import json
import urlparse

import requests

import ims.common.constants as constants
import ims.exception.haas_exceptions as haas_exceptions


class HaaS:
    class Request:
        def __init__(self, method, data, auth=None):
            self.method = method
            self.data = json.dumps(data)
            self.auth = None
            if auth:
                self.auth = auth

        def __str__(self):
            return str(
                {"method": str(self.method), "data": self.data,
                 "auth": self.auth})

    class Communicator:
        def __init__(self, url, request):
            self.url = url
            self.request = request

        def send_request(self):
            try:
                if self.request.method == "get":
                    return self.resp_parse(
                        requests.get(self.url, auth=self.request.auth))
                if self.request.method == "post":
                    return self.resp_parse(
                        requests.post(self.url, data=self.request.data,
                                      auth=self.request.auth))
            except requests.RequestException:
                raise haas_exceptions.ConnectionException()

        def resp_parse(self, obj):
            if obj.status_code == 200:
                try:
                    return {constants.STATUS_CODE_KEY: obj.status_code,
                            constants.RETURN_VALUE_KEY: obj.json()}
                except ValueError:
                    return {constants.STATUS_CODE_KEY: obj.status_code}
            elif obj.status_code > 200 and obj.status_code < 400:
                return {constants.STATUS_CODE_KEY: obj.status_code}
            elif obj.status_code == 401:
                raise haas_exceptions.AuthenticationFailedException()
            elif obj.status_code == 403:
                raise haas_exceptions.AuthorizationFailedException()
            elif obj.status_code >= 400:
                raise haas_exceptions.UnknownException(obj.status_code,
                                                       obj.json()[
                                                           constants.MESSAGE_KEY])

    def __init__(self, base_url, usr, passwd):
        self.base_url = base_url
        self.usr = usr
        self.passwd = passwd

    def __call_rest_api(self, api):
        link = urlparse.urljoin(self.base_url, api)
        request = HaaS.Request('get', None, auth=(self.usr, self.passwd))
        return HaaS.Communicator(link, request).send_request()

    def __call_rest_api_with_body(self, api, body):
        link = urlparse.urljoin(self.base_url, api)
        request = HaaS.Request('post', body, auth=(self.usr, self.passwd))
        return HaaS.Communicator(link, request).send_request()

    def list_free_nodes(self):
        api = 'free_nodes'
        return self.__call_rest_api(api=api)

    def query_project_nodes(self, project):
        api = '/project/' + project + '/nodes'
        return self.__call_rest_api(api=api)

    def detach_node_from_project(self, project, node):
        api = 'project/' + project + '/detach_node'
        body = {"node": node}
        return self.__call_rest_api_with_body(api=api, body=body)

    def attach_node_to_project_network(self, node,
                                       network,
                                       channel,
                                       nic):
        api = '/node/' + node + '/nic/' + nic + '/connect_network'
        body = {"network": network, "channel": channel}
        return self.__call_rest_api_with_body(api=api, body=body)

    def attach_node_haas_project(self, project, node):
        api = 'project/' + project + '/connect_node'
        body = {"node": node}
        return self.__call_rest_api_with_body(api=api, body=body)

    def detach_node_from_project_network(self, node,
                                         network, nic):
        api = '/node/' + node + '/nic/' + nic + '/detach_network'
        body = {"network": network}
        return self.__call_rest_api_with_body(api=api, body=body)

    def get_node_mac_addr(self, node):
        '''
        Checks the current information for the node and returns a tuple consisting of (<project_name>,List of <{"network": network-name}>, NIC name)
        '''
        api = "node/" + node
        node_info = self.__call_rest_api(api)
        #Assuming the first item in nic list is the one being used.
        return node_info[constants.RETURN_VALUE_KEY]['nics'][0]['macaddr']

    def validate_project(self, project):
        api = '/project/' + project + '/nodes'
        return self.__call_rest_api(api=api)
