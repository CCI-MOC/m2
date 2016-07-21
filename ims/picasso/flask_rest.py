import json

from flask import Flask
from flask import request

from ims.rpc.client.rpcclient import *

app = Flask(__name__)

rpc_client = None


def start():
    global rpc_client
    rpc_client = RPCClient()
    cfg = config.get()
    app.run(host=cfg.bind_ip, port=cfg.bind_port)


@app.route('/list_images/', methods=['POST'])
def list_images():
    '''List the images for a project.
    '''
    if request.method == "POST":
        try:
            credentials = extract_credentials(request)
            if credentials is None:
                return "No Authentication Details Given", 400
            list_return = rpc_client.execute_command(
                constants.LIST_IMAGES_COMMAND, credentials, [])
            print list_return
            status_code = list_return[constants.STATUS_CODE_KEY]
            if status_code == 200:
                image_list = list_return[constants.RETURN_VALUE_KEY]
                return json.dumps(image_list), 200
            else:
                return json.dumps(list_return[constants.MESSAGE_KEY]), \
                       list_return[constants.STATUS_CODE_KEY]
        except Exception as ex:
            import traceback
            traceback.print_exc(ex)
    else:
        return 'Please use a POST', 444


@app.route("/provision/", methods=['PUT'])
def provision():
    '''
    Node is the physical node name that we get from HaaS
    '''
    print "Got provision"
    if request.method == "PUT":
        credentials = extract_credentials(request)
        if credentials is None:
            return "No Authentication Details Given", 400
        node_name = request.form[constants.NODE_NAME_PARAMETER]
        img_name = request.form[constants.IMAGE_NAME_PARAMETER]
        network = request.form[constants.NETWORK_PARAMETER]
        channel = request.form[constants.CHANNEL_PARAMETER]
        nic = request.form[constants.NIC_PARAMETER]
        ret = rpc_client.execute_command(constants.PROVISION_COMMAND,
                                         credentials,
                                         [node_name, img_name,
                                          network, channel, nic])
        if ret[constants.STATUS_CODE_KEY] == 200:
            return "Success", 200
        else:
            return ret[constants.MESSAGE_KEY], ret[constants.STATUS_CODE_KEY]
    else:
        return 'Please use a PUT', 444


@app.route("/deprovision/", methods=['DELETE'])
def deprovision():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.method == "DELETE":
        credentials = extract_credentials(request)
        if credentials is None:
            return "No Authentication Details Given", 400
        node_name = request.form[constants.NODE_NAME_PARAMETER]
        network = request.form[constants.NETWORK_PARAMETER]
        nic = request.form[constants.NIC_PARAMETER]
        ret = rpc_client.execute_command(constants.DEPROVISION_COMMAND,
                                         credentials, [node_name, network, nic])
        print ret
        if ret[constants.STATUS_CODE_KEY] == 200:
            return "Success", 200
        else:
            return ret[constants.MESSAGE_KEY], ret[constants.STATUS_CODE_KEY]
    else:
        return 'Please use a DELETE', 444


@app.route("/create_snapshot/", methods=['PUT'])
def create_snapshot():
    '''
    Node is the physical node that you want to dissociate
    '''
    if request.method == "PUT":
        credentials = extract_credentials(request)
        if credentials is None:
            return "No Authentication Details Given", 400
        node_name = request.form[constants.NODE_NAME_PARAMETER]
        snap_name = request.form[constants.SNAP_NAME_PARAMETER]
        ret = rpc_client.execute_command(constants.CREATE_SNAPSHOT_COMMAND,
                                         credentials, [node_name,
                                                       snap_name])
        if ret[constants.STATUS_CODE_KEY] == 200:
            return "Success", 200
        else:
            return ret[constants.MESSAGE_KEY], ret[constants.STATUS_CODE_KEY]
    else:
        return 'Please use a PUT', 444


@app.route("/list_snapshots/", methods=['POST'])
def list_snapshots():
    '''
    List all snapshots for the given image
    '''
    if request.method == "POST":
        credentials = extract_credentials(request)
        if credentials is None:
            return "No Authentication Details Given", 400
        ret = rpc_client.execute_command(constants.LIST_SNAPSHOTS_COMMAND,
                                         credentials, [])
        if ret[constants.STATUS_CODE_KEY] == 200:
            return json.dumps(ret[constants.RETURN_VALUE_KEY]), 200
        else:
            return ret[constants.MESSAGE_KEY], ret[constants.STATUS_CODE_KEY]
    else:
        return "Please use a POST", 444


@app.route("/remove_snapshot/", methods=['DELETE'])
@app.route("/remove_image/", methods=['DELETE'])
def remove_image():
    '''
    Removes the given snapshot for the given image
    '''
    if request.method == "DELETE":
        credentials = extract_credentials(request)
        if credentials is None:
            return "No Authentication Details Given", 400
        img_name = request.form[constants.IMAGE_NAME_PARAMETER]
        ret = rpc_client.execute_command(constants.REMOVE_IMAGE_COMMAND,
                                         credentials,
                                         [img_name])
        if ret[constants.STATUS_CODE_KEY] == 200:
            return "Success", 200
        else:
            return ret[constants.MESSAGE_KEY], ret[constants.STATUS_CODE_KEY]
    else:
        return 'Please use a DELETE', 444


def extract_credentials(request):
    base64_str = request.headers.get('Authorization')
    if base64_str is not None:
        base64_str = base64_str.split(' ')[1]
        project = request.form[constants.PROJECT_PARAMETER]
        return base64_str, project
    else:
        return None
