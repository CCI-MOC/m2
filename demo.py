import json
import urlparse

import requests


class HaaS:
    class Request:
        def __init__(self, method, data, auth=None):
            self.method = method
            self.data = json.dumps(data)
            self.auth = None
            if auth:
                self.auth = auth

    class Communicator:
        def __init__(self, url, request):
            self.url = url
            self.request = request

        def send_request(self):
            if self.request.method == "get":
                requests.get(self.url, auth=self.request.auth).text()
            if self.request.method == "post":
                requests.post(self.url, data=self.request.data,
                              auth=self.request.auth).text()

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

    def query_project_nodes(self, project):
        api = '/project/' + project + '/nodes'
        return self.__call_rest_api(api=api)

    def detach_node_from_project(self, project, node):
        api = 'project/' + project + '/detach_node'
        body = {"node": node}
        return self.__call_rest_api_with_body(api=api, body=body)

    def attach_node_to_project_network(self, node, network, channel, nic):
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

    def node_power_cycle(self, node):
        api = '/node/' + node + "/power_cycle"
        return self.__call_rest_api(api=api)
