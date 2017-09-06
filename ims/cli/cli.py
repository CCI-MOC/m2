#!/usr/bin/python

import json
import sys

import click
import os
import requests
from prettytable import PrettyTable

import ims.common.config as config
import ims.common.constants as constants

config.load()

from ims.einstein.operations import BMI
from ims.exception.exception import BMIException

_cfg = config.get()

_url = "http://{0}:{1}/".format(_cfg.rest_api.ip,
                                _cfg.rest_api.port)

if constants.HIL_USERNAME_VARIABLE in os.environ:
    _username = os.environ[constants.HIL_USERNAME_VARIABLE]
else:
    click.echo(constants.HIL_USERNAME_VARIABLE + " Variable Not Set")
    sys.exit(1)

if constants.HIL_PASSWORD_VARIABLE in os.environ:
    _password = os.environ[constants.HIL_PASSWORD_VARIABLE]
else:
    click.echo(constants.HIL_PASSWORD_VARIABLE + " Variable Not Set")
    sys.exit(1)


def bmi_exception_wrapper(func):
    def function_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BMIException as e:
            click.echo(str(e))

    return function_wrapper


@click.group()
def cli():
    """
    The Bare Metal Imaging (BMI) is a core component of the Massachusetts Open
    Cloud and a image management system(ims) that

    \b
    (1) Provisions numerous nodes as quickly as possible while preserving
    support for multitenancy using Hardware Isolation Layer (HIL) and

    \b
    (2) Introduces the image management techniques that are supported by
    virtual machines, with little to no impact on application performance.
    """
    pass


@cli.command(name='pro', short_help="Provision a Node")
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def provision(project, node, img, network, nic):
    """
    Provision a Node

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    NODE    = The Node to Provision
    IMG     = The Name of the Image to Provision
    NETWORK = The Name of the Provisioning Network
    CHANNEL = The Channel to Provision On (For HIL It is 'vlan/native')
    NIC     = The NIC to use for Network Boot (For HIL IT is 'enp130s0f0')
    """
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.IMAGE_NAME_PARAMETER: img,
            constants.NETWORK_PARAMETER: network,
            constants.NIC_PARAMETER: nic}
    res = requests.put(_url + "provision/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@cli.command(name='dpro', short_help='Deprovision a node')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def deprovision(project, node, network, nic):
    """
    Deprovision a Node

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    NODE    = The Node to Provision
    NETWORK = The Name of the Provisioning Network
    NIC     = The NIC that was used for Network Boot
    """
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.NETWORK_PARAMETER: network,
            constants.NIC_PARAMETER: nic}
    res = requests.delete(_url + "deprovision/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(name='showpro',
             short_help='Lists Provisioned Nodes')
@click.argument(constants.PROJECT_PARAMETER)
@bmi_exception_wrapper
def list_provisioned_nodes(project):
    """
    Lists Provisioned Nodes under a Project.

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    """
    with BMI(_username, _password, project) as bmi:
        table = PrettyTable(field_names=["Node", "Provisioned Image"])
        ret = bmi.list_provisioned_nodes()
        if ret[constants.STATUS_CODE_KEY] == 200:
            for clone in ret[constants.RETURN_VALUE_KEY]:
                table.add_row(clone)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='rm', short_help='Remove an Image')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def remove_image(project, img):
    """
    Remove an Image From BMI

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    IMG     = The Image Name to Remove
    """
    data = {constants.PROJECT_PARAMETER: project,
            constants.IMAGE_NAME_PARAMETER: img}
    res = requests.delete(_url + "remove_image/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(name='ls', short_help='List Images Stored')
@click.argument(constants.PROJECT_PARAMETER)
def list_images(project):
    """
    Lists Images Under A Project

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    """
    data = {constants.PROJECT_PARAMETER: project}
    res = requests.post(_url + "list_images/", data=data,
                        auth=(_username, _password))
    if res.status_code == 200:
        images = json.loads(res.content)
        table = PrettyTable(field_names=["Image"])
        for image in images:
            table.add_row([image])
        click.echo(table.get_string())
    else:
        click.echo(res.content)


@cli.group(short_help='Snapshot Related Commands')
def snap():
    """
    Use The Subcommands under this command to manipulate Snapshots
    """
    pass


@snap.command(name='create', short_help='Create Snapshot')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def create_snapshot(project, node, snap_name):
    """
    Create a Snapshot of a Node's state to preserve it

    \b
    WARNING : The Node must be in a powered down state

    \b
    Arguments:
    PROJECT   = The HIL Project attached to your credentials
    NODE      = The Name of Node to Snapshot
    SNAP_NAME = The Name which needs to be used for saving snapshot
    """
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.SNAP_NAME_PARAMETER: snap_name}
    res = requests.put(_url + "create_snapshot/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@snap.command(name='ls', short_help='List All Snapshots Stored')
@click.argument(constants.PROJECT_PARAMETER)
def list_snapshots(project):
    """
    Lists All The Snapshots Under a Project

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    """
    data = {constants.PROJECT_PARAMETER: project}
    res = requests.post(_url + "list_snapshots/", data=data,
                        auth=(_username, _password))
    if res.status_code == 200:
        snapshots = json.loads(res.content)
        table = PrettyTable(field_names=["Snapshot", "Parent"])
        for snapshot in snapshots:
            table.add_row(snapshot)
        click.echo(table.get_string())
    else:
        click.echo(res.content)


@snap.command(name='rm', short_help='Remove a Snapshot')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def remove_snapshot(project, snap_name):
    """
    Remove a Snapshot under a Project

    \b
    Arguments:
    PROJECT   = The HIL Project attached to your credentials
    SNAP_NAME = The Name of Snapshot that should be Removed.
    """
    data = {constants.PROJECT_PARAMETER: project,
            constants.IMAGE_NAME_PARAMETER: snap_name}
    res = requests.delete(_url + "remove_image/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.group(name='project', help='Project Related Commands')
def project_grp():
    """
    Use The Subcommands under this command to manipulate Projects
    """
    pass


@project_grp.command(name='ls', short_help='Lists Projects')
@bmi_exception_wrapper
def list_projects():
    """
    Lists Projects From DB

    \b
    WARNING = User Must be An Admin
    """
    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.list_projects()
        if ret[constants.STATUS_CODE_KEY] == 200:
            table = PrettyTable(
                field_names=["Id", "Name", "Provision Network"])
            projects = ret[constants.RETURN_VALUE_KEY]
            for project in projects:
                table.add_row(project)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@project_grp.command(name='create', help='Create Project')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.option('--id', default=None, help='Specify what id to use for project')
@bmi_exception_wrapper
def add_project(project, network, id):
    """
    Create Project in DB

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT = The Name of Project (A HIL Project must exist)
    NETWORK = The Name of the Provisioning Network
    """
    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.add_project(project, network, id)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@project_grp.command(name='rm', help='Deletes Project From DB')
@click.argument(constants.PROJECT_PARAMETER)
@bmi_exception_wrapper
def delete_project(project):
    """
    Remove Project From DB

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT = The Name of Project (A HIL Project must exist)
    """
    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.delete_project(project)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.group(help='DB Related Commands')
def db():
    """
    Use The Subcommands under this command to manipulate DB
    """
    pass


@db.command(name='rm', help='Deletes Image From DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@bmi_exception_wrapper
def delete_image(project, img):
    """
    Delete Image in DB

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT = The Name of Project
    IMG     = The Name of the Image to insert
    """
    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.delete_image(project, img)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@db.command(name='create', help='Adds Image to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--id', default=None, help='Specify what id to use for image')
@click.option('--snap', is_flag=True, help='If image is snapshot')
@click.option('--parent', default=None, help='Specify parent name')
@click.option('--public', is_flag=True, help='If image is public')
@bmi_exception_wrapper
def add_image(project, img, id, snap, parent, public):
    """
    Create Image in DB

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT = The Name of Project (A HIL Project must exist)
    IMG = The Name of the Image to insert
    """
    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.add_image(project, img, id, snap, parent, public)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@db.command(name='ls', short_help='Lists All Images')
@click.option('-s', is_flag=True, help='Filter for Snapshots')
@click.option('-c', is_flag=True, help='Filter for Clones')
@click.option('-p', is_flag=True, help='Filter For Public Images')
@click.option('--project', default=None, help='Filter By Project')
@click.option('--name', default=None, help='Filter By Name')
@click.option('--ceph', default=None, help="Filter By Ceph Name")
@bmi_exception_wrapper
def list_all_images(s, c, p, project, name, ceph):
    """
    List All Image Present in DB

    \b
    WARNING = User Must be An Admin
    """

    def second_filter():
        if project is None:
            f1 = True
        else:
            f1 = image[2] == project

        if ceph is None:
            f2 = True
        else:
            f2 = image[3] == ceph

        if name is None:
            f3 = True
        else:
            f3 = image[1] == name

        f4 = project is None and ceph is None and name is None

        return (f1 and f2 and f3) or f4

    with BMI(_username, _password, constants.BMI_ADMIN_PROJECT) as bmi:
        ret = bmi.list_all_images()
        if ret[constants.STATUS_CODE_KEY] == 200:
            table = PrettyTable(
                field_names=["Id", "Name", "Project", "Ceph", "Public",
                             "Snapshot",
                             "Parent"])
            images = ret[constants.RETURN_VALUE_KEY]
            for image in images:
                flag = False
                if s and image[5]:
                    flag = second_filter()
                elif c and image[6] != '' and not image[5]:
                    flag = second_filter()
                elif p and image[4]:
                    flag = second_filter()
                elif not s and not c and not p:
                    flag = second_filter()

                if flag:
                    table.add_row(image)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='import', short_help='Import an Image or Snapshot into BMI')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--snap', default=None, help='Specifies what snapshot to import')
@click.option('--protect', is_flag=True,
              help="Set if snapshot should be protected before cloning")
@bmi_exception_wrapper
def import_ceph_image(project, img, snap, protect):
    """
    Import an existing CEPH image into BMI

    \b
    Arguments:
    PROJECT = The HIL Project attached to your credentials
    IMG = The Name of the CEPH Image to import
    """
    with BMI(_username, _password, project) as bmi:
        ret = None
        if snap is None:
            ret = bmi.import_ceph_image(img)
        else:
            ret = bmi.import_ceph_snapshot(img, snap, protect)

        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='export', short_help='Export a BMI image to ceph')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument('name')
@bmi_exception_wrapper
def export_ceph_image(project, img, name):
    """
    """
    with BMI(_username, _password, project) as bmi:
        ret = bmi.export_ceph_image(img, str(name))
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='cp', help="Copy an existing image not clones")
@click.argument(constants.SRC_PROJECT_PARAMETER)
@click.argument(constants.IMAGE1_NAME_PARAMETER)
@click.argument(constants.DEST_PROJECT_PARAMETER)
@click.argument(constants.IMAGE2_NAME_PARAMETER, default=None)
@bmi_exception_wrapper
def copy_image(src_project, img1, dest_project, img2):
    """
    Copy an image from one project to another

    \b
    Arguments:
    SRC_PROJECT  = The HIL Project attached to your credentials
    IMG1         = The Name of the source image
    DEST_PROJECT = The Destination HIL Project (Can be same as source)
    IMG2         = The Name of the destination image (optional)
    """
    with BMI(_username, _password, src_project) as bmi:
        ret = bmi.copy_image(img1, dest_project, img2)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='mv', help='Move Image From Project to Another')
@click.argument(constants.SRC_PROJECT_PARAMETER)
@click.argument(constants.IMAGE1_NAME_PARAMETER)
@click.argument(constants.DEST_PROJECT_PARAMETER)
@click.argument(constants.IMAGE2_NAME_PARAMETER, default=None)
@bmi_exception_wrapper
def move_image(src_project, img1, dest_project, img2):
    """
    Move an image from one project to another

    \b
    Arguments:
    SRC_PROJECT  = The HIL Project attached to your credentials
    IMG1         = The Name of the source image
    DEST_PROJECT = The Destination HIL Project (Can be same as source)
    IMG2         = The Name of the destination image (optional)
    """
    with BMI(_username, _password, src_project) as bmi:
        ret = bmi.move_image(img1, dest_project, img2)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.group(name='node', help='Node Related Commands')
def node():
    pass


@node.command('ip', help='Get IP on Provisioning Network')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@bmi_exception_wrapper
def get_node_ip(project, node):
    """
    Get the IP of Provisioned Node on Provisioning Network

    \b
    Arguments:
    PROJECT  = The HIL Project attached to your credentials
    NODE     = The node whose IP is required
    """
    with BMI(_username, _password, project) as bmi:
        ret = bmi.get_node_ip(node)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo(ret[constants.RETURN_VALUE_KEY])
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.group(help='ISCSI Related Commands')
def iscsi():
    pass


@iscsi.command(name='create', help='Create ISCSI Mapping')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@bmi_exception_wrapper
def create_mapping(project, img):
    """
    Mount image on iscsi server

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT  = The HIL Project attached to your credentials
    IMG      = The image that must be mounted
    """
    with BMI(_username, _password, project) as bmi:
        ret = bmi.mount_image(img)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo('Success')
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@iscsi.command(name='rm', help='Remove ISCSI Mapping')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@bmi_exception_wrapper
def delete_mapping(project, img):
    """
    Unmount image from iscsi server

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT  = The HIL Project attached to your credentials
    IMG      = The image that must be unmounted
    """
    with BMI(_username, _password, project) as bmi:
        ret = bmi.umount_image(img)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo('Success')
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@iscsi.command(name='ls', help='Show ISCSI Mappings')
@click.argument(constants.PROJECT_PARAMETER)
@bmi_exception_wrapper
def show_mappings(project):
    """
    Show mounted images on iscsi

    \b
    WARNING = User Must be An Admin

    \b
    Arguments:
    PROJECT  = The HIL Project attached to your credentials
    """
    # with BMI(_username, _password, project) as bmi:
    #     ret = bmi.show_mounted()
    #     if ret[constants.STATUS_CODE_KEY] == 200:
    #         table = PrettyTable(field_names=['Target', 'Block Device'])
    #         mappings = ret[constants.RETURN_VALUE_KEY]
    #         for k, v in mappings.iteritems():
    #             table.add_row([k, v])
    #         click.echo(table.get_string())
    #     else:
    #         click.echo(ret[constants.MESSAGE_KEY])
    click.echo("Need to Re-Implement")


@cli.command(name='upload', help='Upload Image to BMI')
def upload():
    """
    Coming Soon
    """
    click.echo('Not Yet Implemented')


@cli.command(name='download', help='Download Image from BMI')
def download():
    """
    Coming Soon
    """
    click.echo('Not Yet Implemented')


if __name__ == '__main__':
    cli()
