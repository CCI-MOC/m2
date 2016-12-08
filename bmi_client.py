import urlparse

import requests

NODE_NAME_PARAMETER = 'node'
IMAGE_NAME_PARAMETER = "img"
SNAP_NAME_PARAMETER = "snap_name"
PROJECT_PARAMETER = "project"
NETWORK_PARAMETER = "network"
NIC_PARAMETER = "nic"
CHANNEL_PARAMETER = "channel"


class BMI:
    class Request:
        def __init__(self, method, data, auth=None):
            self.method = method
            self.data = data
            self.auth = None
            if auth:
                self.auth = auth

    class Communicator:
        def __init__(self, url, request):
            self.url = url
            self.request = request

        def send_request(self):
            if self.request.method == "put":
                requests.put(self.url, auth=self.request.auth).text()
            if self.request.method == "delete":
                requests.delete(self.url, data=self.request.data,
                              auth=self.request.auth).text()

    def __init__(self, base_url, project, usr, passwd):
        self.base_url = base_url
        self.project = project
        self.usr = usr
        self.passwd = passwd

    def __call_rest_api_with_put(self, api, body):
        link = urlparse.urljoin(self.base_url, api)
        request = BMI.Request('put', body, auth=(self.usr, self.passwd))
        return BMI.Communicator(link, request).send_request()

    def __call_rest_api_with_delete(self, api, body):
        link = urlparse.urljoin(self.base_url, api)
        request = BMI.Request('delete', body, auth=(self.usr, self.passwd))
        return BMI.Communicator(link, request).send_request()

    def provision(self, node, image, network, channel, nic):
        api = '/provision'
        data = {PROJECT_PARAMETER: self.project,
                NODE_NAME_PARAMETER: node,
                IMAGE_NAME_PARAMETER: image,
                NETWORK_PARAMETER: network,
                CHANNEL_PARAMETER: channel,
                NIC_PARAMETER: nic}
        self.__call_rest_api_with_put(api=api, body=data)

    def deprovision(self, node, network, nic):
        api = '/deprovision'
        data = {PROJECT_PARAMETER: self.project,
                NODE_NAME_PARAMETER: node,
                NETWORK_PARAMETER: network,
                NIC_PARAMETER: nic}
        self.__call_rest_api_with_delete(api=api, body=data)
