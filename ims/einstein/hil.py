import json
import time
import urlparse

import requests

import ims.common.constants as constants
import ims.exception.haas_exceptions as haas_exceptions
from ims.common.log import create_logger, trace, log
from ims.exception.exception import HaaSException

logger = create_logger(__name__)


class HIL:
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
        @trace
        def __init__(self, url, request):
            self.url = url
            self.request = request

        @trace
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

        @trace
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
            elif obj.status_code == 400:
                raise haas_exceptions.NotAttachedException()
            elif obj.status_code == 409:
                error_msg = obj.json()[constants.MESSAGE_KEY]
                if "already attached" in error_msg:
                    raise haas_exceptions.AttachedException()
                raise haas_exceptions.UnknownException(obj.status_code,
                                                       error_msg)
            elif obj.status_code > 400:
                # For PEP8
                error_msg = obj.json()[constants.MESSAGE_KEY]
                raise haas_exceptions.UnknownException(obj.status_code,
                                                       error_msg)

    @log
    def __init__(self, base_url, usr, passwd):
        self.base_url = base_url
        self.usr = usr
        self.passwd = passwd

    @trace
    def __call_rest_api(self, api):
        link = urlparse.urljoin(self.base_url, api)
        request = HIL.Request('get', None, auth=(self.usr, self.passwd))
        return HIL.Communicator(link, request).send_request()

    @trace
    def __call_rest_api_with_body(self, api, body):
        link = urlparse.urljoin(self.base_url, api)
        request = HIL.Request('post', body, auth=(self.usr, self.passwd))
        return HIL.Communicator(link, request).send_request()

    @log
    def list_free_nodes(self):
        api = 'free_nodes'
        return self.__call_rest_api(api=api)

    @log
    def query_project_nodes(self, project):
        api = '/project/' + project + '/nodes'
        return self.__call_rest_api(api=api)

    @log
    def detach_node_from_project(self, project, node):
        api = 'project/' + project + '/detach_node'
        body = {"node": node}
        return self.__call_rest_api_with_body(api=api, body=body)

    @log
    def attach_node_to_project_network(self, node, network, nic):
        try:
            api = '/node/' + node + '/nic/' + nic + '/connect_network'
            body = {"network": network, "channel": constants.HAAS_BMI_CHANNEL}
            return self.__call_rest_api_with_body(api=api, body=body)
        except haas_exceptions.AttachedException:
            logger.info("%s is already attached to %s at %s" % (node,
                                                                network,
                                                                nic))

    @log
    def attach_node_haas_project(self, project, node):
        api = 'project/' + project + '/connect_node'
        body = {"node": node}
        return self.__call_rest_api_with_body(api=api, body=body)

    @log
    def detach_node_from_project_network(self, node, network, nic):
        try:
            api = '/node/' + node + '/nic/' + nic + '/detach_network'
            body = {"network": network}
            return self.__call_rest_api_with_body(api=api, body=body)
        except haas_exceptions.NotAttachedException:
            logger.info("%s is already detached to %s at %s" % (node,
                                                                network,
                                                                nic))

    @log
    def get_node_mac_addr(self, node):
        api = "node/" + node
        node_info = self.__call_rest_api(api)
        logger.debug("The Node Info = %s", node_info)
        return node_info[constants.RETURN_VALUE_KEY]['nics'][0]['macaddr']

    @log
    def validate_project(self, project):
        api = '/project/' + project + '/nodes'
        return self.__call_rest_api(api=api)

    @log
    def wait(self, node, network, nic, attaching=True):
        while True:
            try:
                if attaching:
                    self.attach_node_to_project_network(node, network, nic)
                else:
                    self.detach_node_from_project_network(node, network, nic)
                break
            except haas_exceptions.UnknownException:
                time.sleep(0)
