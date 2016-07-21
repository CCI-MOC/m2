#!/usr/bin/python

import json

import click
import requests
from prettytable import PrettyTable

import ims.common.config as config
import ims.common.constants as constants

config.load()

from ims.einstein.operations import BMI
from ims.database import *

_cfg = config.get()

_url = "http://{0}:{1}/".format(_cfg.bind_ip, _cfg.bind_port)

_username = os.environ[constants.HAAS_USERNAME_VARIABLE]
_password = os.environ[constants.HAAS_PASSWORD_VARIABLE]


@click.group()
def cli():
    pass


@cli.command(name='pro',
             help="Provisions a <NODE> with an <IMAGE> connected on <NIC> to <NETWORK> through <CHANNEL>")
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.CHANNEL_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def provision(project, node, img, network, channel, nic):
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.IMAGE_NAME_PARAMETER: img,
            constants.NETWORK_PARAMETER: network,
            constants.CHANNEL_PARAMETER: channel,
            constants.NIC_PARAMETER: nic}
    res = requests.put(_url + "provision/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@cli.command(name='dpro',
             help='Deprovision <NODE> from <NETWORK> connected on <NIC>')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def deprovision(project, node, network, nic):
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.NETWORK_PARAMETER: network,
            constants.NIC_PARAMETER: nic}
    res = requests.delete(_url + "deprovision/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(name='showpro', help='Shows All Provisioned Nodes')
@click.argument(constants.PROJECT_PARAMETER)
def list_provisioned_nodes(project):
    with BMI(_username, _password, project) as bmi:
        table = PrettyTable(field_names=["Node", "Provisioned Image"])
        ret = bmi.list_provisioned_nodes()
        if ret[constants.STATUS_CODE_KEY] == 200:
            for clone in ret[constants.RETURN_VALUE_KEY]:
                table.add_row(clone)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='rm', help='Remove <IMAGE>')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def remove_image(project, img):
    data = {constants.PROJECT_PARAMETER: project,
            constants.IMAGE_NAME_PARAMETER: img}
    res = requests.delete(_url + "remove_image/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(name='ls', help='List Images Stored')
@click.argument(constants.PROJECT_PARAMETER)
def list_images(project):
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


@cli.group(help='Snapshot Related Commands')
def snap():
    pass


@snap.command(name='create', help='Create Snapshot of <NODE> as <SNAP_NAME>')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def create_snapshot(project, node, snap_name):
    data = {constants.PROJECT_PARAMETER: project,
            constants.NODE_NAME_PARAMETER: node,
            constants.SNAP_NAME_PARAMETER: snap_name}
    res = requests.put(_url + "create_snapshot/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@snap.command(name='ls', help='List All Snapshots Stored')
@click.argument(constants.PROJECT_PARAMETER)
def list_snapshots(project):
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


@snap.command(name='rm', help='Remove the given Snapshot')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def remove_snapshot(project, snap_name):
    data = {constants.PROJECT_PARAMETER: project,
            constants.IMAGE_NAME_PARAMETER: snap_name}
    res = requests.delete(_url + "remove_image/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.group(name='project', help='Project Related Commands')
def project_grp():
    pass


@project_grp.command(name='ls', help='Lists Projects in DB')
def list_projects():
    with BMI(_username, _password, "bmi_admin") as bmi:
        ret = bmi.list_projects()
        if ret[constants.STATUS_CODE_KEY] == 200:
            table = PrettyTable(field_names=["Id", "Name", "Provision Network"])
            projects = ret[constants.RETURN_VALUE_KEY]
            for project in projects:
                table.add_row(project)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@project_grp.command(name='create', help='Adds Project to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.option('--id', default=None, help='Specify what id to use for project')
def add_project(project, network, id):
    with BMI(_username, _password, "bmi_admin") as bmi:
        ret = bmi.add_project(project, network, id)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@project_grp.command(name='rm', help='Deletes Project From DB')
@click.argument(constants.PROJECT_PARAMETER)
def delete_project(project):
    with BMI(_username, _password, "bmi_admin") as bmi:
        ret = bmi.delete_project(project)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.group(help='DB Related Commands')
def db():
    pass


@db.command(name='rm', help='Deletes Image From DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def delete_image(project, img):
    with BMI(_username, _password, project) as bmi:
        ret = bmi.delete_image(img)
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
def add_image(project, img, id, snap, parent, public):
    with BMI(_username, _password, project) as bmi:
        ret = bmi.add_image(img, id, snap, parent, public)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@db.command(name='ls', help='Lists All Images')
def list_all_images():
    with BMI(_username, _password, "bmi_admin") as bmi:
        ret = bmi.list_all_images()
        if ret[constants.STATUS_CODE_KEY] == 200:
            table = PrettyTable(
                field_names=["Id", "Name", "Project Name", "Is Public",
                             "Is Snapshot",
                             "Parent"])
            images = ret[constants.RETURN_VALUE_KEY]
            for image in images:
                table.add_row(image)
            click.echo(table.get_string())
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='import',
             help='Clones an existing ceph image and makes it compatible with BMI')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--snap', default=None, help='Specifies what snapshot to import')
def import_ceph_image(project, img, snap):
    with BMI(_username, _password, project) as bmi:
        ret = None
        if snap is None:
            ret = bmi.import_ceph_image(img)
        else:
            ret = bmi.import_ceph_snapshot(img, snap)

        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='cp', help="Copy an existing image not clones")
@click.argument('src_project')
@click.argument('img1')
@click.argument('dest_project')
@click.argument('img2', default=None)
def copy_image(src_project, img1, dest_project, img2):
    with BMI(_username, _password, src_project) as bmi:
        ret = bmi.copy_image(img1, dest_project, img2)
        if ret[constants.STATUS_CODE_KEY] == 200:
            click.echo("Success")
        else:
            click.echo(ret[constants.MESSAGE_KEY])


@cli.command(name='mv', help='Move Image From Project to Another')
@click.argument('src_project')
@click.argument('img1')
@click.argument('dest_project')
@click.argument('img2', default=None)
def move_image(src_project, img1, dest_project, img2):
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
def get_node_ip(project, node):
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
def create_mapping(project, img):
    click.echo('Not Yet Implemented')


@iscsi.command(name='rm', help='Remove ISCSI Mapping')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def delete_mapping(project, img):
    click.echo('Not Yet Implemented')


@iscsi.command(name='ls', help='Show ISCSI Mappings')
def show_mappings():
    click.echo('Not Yet Implemented')


@cli.command(name='upload', help='Upload Image to BMI')
def upload():
    click.echo('Not Yet Implemented')


@cli.command(name='download', help='Download Image from BMI')
def download():
    click.echo('Not Yet Implemented')


if __name__ == '__main__':
    cli()
