#!/usr/bin/python

import click
import requests
from prettytable import PrettyTable

import ims.common.config as config
import ims.common.constants as constants

config.load()

from ims.database import *
import ims.einstein.ceph as ceph

_cfg = config.get()

_url = "http://{0}:{1}/".format(_cfg.bind_ip, _cfg.bind_port)

_project = os.environ[constants.PROJECT_ENV_VARIABLE]
_username = os.environ[constants.HAAS_USERNAME_VARIABLE]
_password = os.environ[constants.HAAS_PASSWORD_VARIABLE]


@click.group()
def cli():
    pass


@cli.command(
    help="Provisions a <NODE> with an <IMAGE> connected on <NIC> to <NETWORK> through <CHANNEL>")
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.CHANNEL_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def provision(node, img, network, channel, nic):
    data = {constants.PROJECT_PARAMETER: _project,
            constants.NODE_NAME_PARAMETER: node,
            constants.IMAGE_NAME_PARAMETER: img,
            constants.NETWORK_PARAMETER: network,
            constants.CHANNEL_PARAMETER: channel,
            constants.NIC_PARAMETER: nic}
    res = requests.put(_url + "provision/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@cli.command(help='Deprovision <NODE> from <NETWORK> connected on <NIC>')
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def deprovision(node, network, nic):
    data = {constants.PROJECT_PARAMETER: _project,
            constants.NODE_NAME_PARAMETER: node,
            constants.NETWORK_PARAMETER: network,
            constants.NIC_PARAMETER: nic}
    res = requests.delete(_url + "deprovision/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(help='Create Snapshot of <NODE> as <SNAP_NAME>')
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def create_snapshot(node, snap_name):
    data = {constants.PROJECT_PARAMETER: _project,
            constants.NODE_NAME_PARAMETER: node,
            constants.SNAP_NAME_PARAMETER: snap_name}
    res = requests.put(_url + "create_snapshot/", data=data,
                       auth=(_username, _password))
    click.echo(res.content)


@cli.command(help='List All Snapshots Stored')
def list_snapshots():
    data = {constants.PROJECT_PARAMETER: _project}
    res = requests.post(_url + "list_snapshots/", data=data,
                        auth=(_username, _password))
    click.echo(res.content)


@cli.command(help='Remove <IMAGE>')
@click.argument(constants.IMAGE_NAME_PARAMETER)
def remove_image(img):
    data = {constants.PROJECT_PARAMETER: _project,
            constants.IMAGE_NAME_PARAMETER: img}
    res = requests.delete(_url + "remove_image/", data=data, auth=(
        _username, _password))
    click.echo(res.content)


@cli.command(help='List Images Stored')
def list_images():
    data = {constants.PROJECT_PARAMETER: _project}
    res = requests.post(_url + "list_images/", data=data,
                        auth=(_username, _password))
    click.echo(res.content)


# Developer Commands

@cli.group(help='Develpers Commands that can be used')
def dev():
    pass


@dev.command(help='Lists Projects in DB')
def list_projects():
    db = Database()
    projects = db.project.fetch_names()
    table = PrettyTable(field_names=["Id", "Name", "Provision Network"])
    for project in projects:
        table.add_row(project)
    click.echo(table.get_string())
    db.close()


@dev.command(help='Adds Project to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.option('--id', default=-1, help='Specify what id to use for project')
def add_project(project, network, id):
    db = Database()
    if id == -1:
        db.project.insert(project, network)
    else:
        db.project.insert(project, network, id=id)
    click.echo("Success")
    db.close()


@dev.command(help='Deletes Project From DB')
@click.argument(constants.PROJECT_PARAMETER)
def delete_project(project):
    db = Database()
    db.project.delete_with_name(project)
    click.echo("Success")
    db.close()


@dev.command(help='Deletes Image From DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def delete_image(project, img):
    db = Database()
    db.image.delete_with_name_from_project(img, project)
    click.echo("Success")
    db.close()


@dev.command(help='Adds Image to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--id', default=-1, help='Specify what id to use for image')
@click.option('--snap', is_flag=True, help='If image is snapshot')
@click.option('--clone', is_flag=True, help='If image is provision clone')
@click.option('--public', is_flag=True, help='If image is public')
def add_image(project, img, id, snap, clone, public):
    db = Database()
    pid = db.project.fetch_id_with_name(project)
    if id == -1:
        db.image.insert(img, pid, public, snap, clone)
    else:
        db.image.insert(img, pid, public, snap, clone, id=id)
    click.echo("Success")
    db.close()


@dev.command(help='Lists All Images')
@click.argument(constants.PROJECT_PARAMETER)
def list_all_images(project):
    db = Database()
    images = db.image.fetch_all_images_from_project(project)
    table = PrettyTable(
        field_names=["Id", "Name", "Project Name", "Is Public", "Is Snapshot",
                     "Is Provision Clone"])
    for image in images:
        table.add_row(image)
    click.echo(table.get_string())
    db.close()


@dev.command(
    help='Clones an existing ceph image and makes it compatible with BMI')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def convert_ceph_image(project, img):
    fs = ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME])
    db = Database()
    pid = db.project.fetch_id_with_name(project)
    ceph_img_name = str(img)

    fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
    fs.snap_protect(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
    db.image.insert(ceph_img_name, pid)
    snap_ceph_name = __get__ceph_image_name(ceph_img_name, project)
    fs.clone(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME,
             snap_ceph_name)
    fs.flatten(snap_ceph_name)
    fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
    fs.snap_protect(snap_ceph_name,
                    constants.DEFAULT_SNAPSHOT_NAME)
    fs.snap_unprotect(ceph_img_name,
                      constants.DEFAULT_SNAPSHOT_NAME)
    fs.remove_snapshot(ceph_img_name,
                       constants.DEFAULT_SNAPSHOT_NAME)
    click.echo("Success")
    db.close()
    fs.tear_down()


@dev.command(
    help='Clones an existing ceph image snapshot and makes it compatible with BMI')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def convert_ceph_snapshot(project, img, snap_name):
    fs = ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME])
    db = Database()
    pid = db.project.fetch_id_with_name(project)
    ceph_img_name = str(img)

    fs.snap_protect(ceph_img_name, snap_name)
    db.image.insert(ceph_img_name, pid)
    snap_ceph_name = __get__ceph_image_name(ceph_img_name, project)
    fs.clone(ceph_img_name, snap_name,
             snap_ceph_name)
    fs.flatten(snap_ceph_name)
    fs.snap_image(snap_ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
    fs.snap_protect(snap_ceph_name,
                    constants.DEFAULT_SNAPSHOT_NAME)
    db.close()
    fs.tear_down()


def __get__ceph_image_name(name, project):
    db = Database()
    img_id = db.image.fetch_id_with_name_from_project(name, project)
    if img_id is None:
        logger.info("Raising Image Not Found Exception for %s", name)
        raise db_exceptions.ImageNotFoundException(name)

    return str(_cfg.uid) + "img" + str(img_id)


if __name__ == '__main__':
    cli()
