import json

from flask import Flask
from flask import request

import ims.common.config as config
import ims.common.constants as constants
from ims.common.log import create_logger, log, trace
from ims.rpc.client.rpc_client import RPCClient

app = Flask(__name__)
rpc_client = None
logger = create_logger(__name__)


@log
def setup_rpc():
    global rpc_client
    rpc_client = RPCClient()


@log
def start():
    setup_rpc()
    cfg = config.get()
    app.run(host=cfg.rest_api.ip,
            port=cfg.rest_api.port)


@log
def rest_call(path, method, command, parameters):
    def decorator(func):
        app.add_url_rule(path, func.__name__,
                         _rest_wrapper(method, command, parameters),
                         methods=[method])
        return func

    return decorator


@trace
def _extract_credentials(request):
    base64_str = request.headers.get('Authorization')
    if base64_str is not None:
        base64_str = base64_str.split(' ')[1]
        project = request.form[constants.PROJECT_PARAMETER]
        return base64_str, project
    else:
        return None


@trace
def _rest_wrapper(method, command, parameters):
    def wrapper():
        extracted_parameters = []
        if request.method == method:
            credentials = _extract_credentials(request)
            if credentials is None:
                return "No Authentication Details Given", 400
            for parameter in parameters:
                extracted_parameters.append(request.form[parameter])
            ret = rpc_client.execute_command(command, credentials,
                                             extracted_parameters)
            if ret[constants.STATUS_CODE_KEY] == 200:
                ret = json.dumps(ret[constants.RETURN_VALUE_KEY])
                if ret == 'true':
                    return "Success", 200
                else:
                    return ret, 200
            else:
                return ret[constants.MESSAGE_KEY], ret[
                    constants.STATUS_CODE_KEY]
        else:
            return "Please use " + method, 405

    return wrapper


@rest_call("/list_images/", 'POST', constants.LIST_IMAGES_COMMAND, [])
def list_images():
    pass


@rest_call("/provision/", 'PUT', constants.PROVISION_COMMAND,
           [constants.NODE_NAME_PARAMETER, constants.IMAGE_NAME_PARAMETER,
            constants.NETWORK_PARAMETER, constants.NIC_PARAMETER])
def provision():
    pass


@rest_call("/deprovision/", "DELETE", constants.DEPROVISION_COMMAND,
           [constants.NODE_NAME_PARAMETER, constants.NETWORK_PARAMETER,
            constants.NIC_PARAMETER])
def deprovision():
    pass


@rest_call("/create_snapshot/", "PUT", constants.CREATE_SNAPSHOT_COMMAND,
           [constants.NODE_NAME_PARAMETER, constants.SNAP_NAME_PARAMETER])
def create_snapshot():
    pass


@rest_call("/list_snapshots/", "POST", constants.LIST_SNAPSHOTS_COMMAND, [])
def list_snapshots():
    pass


@rest_call("/remove_image/", "DELETE", constants.REMOVE_IMAGE_COMMAND,
           [constants.IMAGE_NAME_PARAMETER])
def remove_image():
    pass
