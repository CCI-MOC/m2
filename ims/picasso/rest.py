# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import json
import os

from ims.rpc.client.rpcclient import *


def list_images():
    '''List the images for a project.
    '''
    if request.env.request_method == "POST":
        try:
            config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
            rpc_client = RPCClient()
            credentials = extract_credentials(request)
            if credentials is None:
                response.status = 400
                response.body = "No Authentication Details Given"
                return response.body
            list_return = rpc_client.execute_command(
                constants.LIST_ALL_IMAGES_COMMAND, credentials, [])
            status_code = list_return[constants.STATUS_CODE_KEY]
            if status_code == 200:
                image_list = list_return[constants.RETURN_VALUE_KEY]
                response.body = json.dumps(image_list)
                return response.body
            else:
                response.status = list_return[constants.STATUS_CODE_KEY]
                response.body = json.dumps(list_return[constants.MESSAGE_KEY])
                return response.body
        except Exception as ex:
            import traceback
            traceback.print_exc(ex)
    else:
        response.status = 444
        return 'Please use a POST'


def provision_node():
    '''
    Node is the physical node name that we get from HaaS
    '''
    if request.env.request_method == "PUT":
        config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
        rpc_client = RPCClient()
        credentials = extract_credentials(request)
        if credentials is None:
            response.status = 400
            response.body = "No Authentication Details Given"
            return response.body
        node_name = request.vars[constants.NODE_NAME_PARAMETER]
        img_name = request.vars[constants.IMAGE_NAME_PARAMETER]
        snap_name = request.vars[constants.SNAP_NAME_PARAMETER]
        network = request.vars[constants.NETWORK_PARAMETER]
        channel = request.vars[constants.CHANNEL_PARAMETER]
        nic = request.vars[constants.NIC_PARAMETER]
        ret = rpc_client.execute_command(constants.PROVISION_COMMAND,
                                         credentials,
                                         [node_name, img_name, snap_name,
                                          network, channel, nic])
        if ret[constants.STATUS_CODE_KEY] == 200:
            response.body = ret[constants.RETURN_VALUE_KEY]
            response.status = 200
            return response.status
        else:
            response.status = ret[constants.STATUS_CODE_KEY]
            response.body = ret[constants.MESSAGE_KEY]
            return response.body
    else:
        response.status = 444
        return 'Please use a PUT'


def remove_node():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.env.request_method == "DELETE":
        config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
        rpc_client = RPCClient()
        credentials = extract_credentials(request)
        if credentials is None:
            response.status = 400
            response.body = "No Authentication Details Given"
            return response.body
        node_name = request.vars[constants.NODE_NAME_PARAMETER]
        network = request.vars[constants.NETWORK_PARAMETER]
        nic = request.vars[constants.NIC_PARAMETER]
        ret = rpc_client.execute_command(constants.DETACH_NODE_COMMAND,
                                         credentials, [node_name, network, nic])
        if ret[constants.STATUS_CODE_KEY] == 200:
            response.body = ret[constants.RETURN_VALUE_KEY]
            response.status = 200
            return response.status
        else:
            response.status = ret[constants.STATUS_CODE_KEY]
            response.body = ret[constants.MESSAGE_KEY]
            return response.body
    else:
        response.status = 444
        return 'Please use a DELETE'


def snap_image():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.env.request_method == "PUT":
        config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
        rpc_client = RPCClient()
        credentials = extract_credentials(request)
        if credentials is None:
            response.status = 400
            response.body = "No Authentication Details Given"
            return response.body
        img_name = request.vars[constants.IMAGE_NAME_PARAMETER]
        snap_name = request.vars[constants.SNAP_NAME_PARAMETER]
        ret = rpc_client.execute_command(constants.CREATE_SNAPSHOT_COMMAND,
                                         credentials, [img_name,
                                                       snap_name])
        if ret[constants.STATUS_CODE_KEY] == 200:
            response.body = ret[constants.RETURN_VALUE_KEY]
            response.status = 200
            return response.status
        else:
            response.status = ret[constants.STATUS_CODE_KEY]
            response.body = ret[constants.MESSAGE_KEY]
            return response.body
    else:
        response.status = 444
        return 'Please use a PUT'


def list_snapshots():
    '''
    List all snapshots for the given image
    '''
    if request.env.request_method == "POST":
        config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
        rpc_client = RPCClient()
        credentials = extract_credentials(request)
        if credentials is None:
            response.status = 400
            response.body = "No Authentication Details Given"
            return response.body
        img_name = request.vars[constants.IMAGE_NAME_PARAMETER]
        ret = rpc_client.execute_command(constants.LIST_SNAPSHOTS_COMMAND,
                                         credentials, [img_name])
        if ret[constants.STATUS_CODE_KEY] == 200:
            response.body = ret[constants.RETURN_VALUE_KEY]
            response.status = 200
            return json.dumps(response.body)
        else:
            response.status = ret[constants.STATUS_CODE_KEY]
            response.body = ret[constants.MESSAGE_KEY]
            return response.body
    else:
        response.status = 444
        return "Please use a POST"


def remove_snapshot():
    '''
    Removes the given snapshot for the given image
    '''
    if request.env.request_method == "DELETE":
        config.load(os.path.join(os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')),
                                     'static/bmiconfig.cfg'))
        rpc_client = RPCClient()
        credentials = extract_credentials(request)
        if credentials is None:
            response.status = 400
            response.body = "No Authentication Details Given"
            return response.body
        img_name = request.vars[constants.IMAGE_NAME_PARAMETER]
        snap_name = request.vars[constants.SNAP_NAME_PARAMETER]
        ret = rpc_client.execute_command(constants.REMOVE_SNAPSHOTS_COMMAND,
                                         credentials,
                                         [img_name, snap_name])
        if ret[constants.STATUS_CODE_KEY] == 200:
            response.body = ret[constants.RETURN_VALUE_KEY]
            response.status = 200
            return response.status
        else:
            response.status = ret[constants.STATUS_CODE_KEY]
            response.body = ret[constants.MESSAGE_KEY]
            return response.body
    else:
        response.status = 444
        return 'Please use a DELETE'


def extract_credentials(request):
    base64_str = request.env.http_authorization
    if base64_str is not None:
        base64_str = base64_str.split(' ')[1]
        project = request.vars[constants.PROJECT_PARAMETER]
        return base64_str, project
    else:
        return None
