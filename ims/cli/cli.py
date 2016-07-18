#!/usr/bin/python

import json

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
    table = PrettyTable(field_names=["Node", "Provisioned Image"])
    with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
        with Database() as db:
            clones = db.image.fetch_clones_from_project(project)
            for clone in clones:
                ceph_name = __get__ceph_image_name(clone, project)
                parent_info = fs.get_parent_info(ceph_name)
                start_index = parent_info[1].find("img")
                start_index += 3
                img_id = parent_info[1][start_index:]
                name = db.image.fetch_name_with_id(img_id)
                table.add_row([clone, name])
    click.echo(table.get_string())


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
    images = json.loads(res.content)
    table = PrettyTable(field_names=["Image"])
    for image in images:
        table.add_row([image])
    click.echo(table.get_string())


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
    snapshots = json.loads(res.content)
    table = PrettyTable(field_names=["Snapshot"])
    for snapshot in snapshots:
        table.add_row([snapshot])
    click.echo(table.get_string())


@snap.command(name='rm', help='Remove the given Snapshot')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def remove_snapshot(project, snapshot):
    remove_image(project, snapshot)


@cli.group(name='project', help='Project Related Commands')
def project_grp():
    pass


@project_grp.command(name='ls', help='Lists Projects in DB')
def list_projects():
    table = PrettyTable(field_names=["Id", "Name", "Provision Network"])
    with Database() as db:
        projects = db.project.fetch_projects()
        for project in projects:
            table.add_row(project)
    click.echo(table.get_string())


@project_grp.command(name='create', help='Adds Project to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.option('--id', default=-1, help='Specify what id to use for project')
def add_project(project, network, id):
    with Database() as db:
        if id == -1:
            db.project.insert(project, network)
        else:
            db.project.insert(project, network, id=id)
    click.echo("Success")


@project_grp.command(name='rm', help='Deletes Project From DB')
@click.argument(constants.PROJECT_PARAMETER)
def delete_project(project):
    with Database() as db:
        db.project.delete_with_name(project)
    click.echo("Success")


@cli.group(help='DB Related Commands')
def db():
    pass


@db.command(name='rm', help='Deletes Image From DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
def delete_image(project, img):
    with Database() as db:
        db.image.delete_with_name_from_project(img, project)
    click.echo("Success")


@db.command(name='create', help='Adds Image to DB')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--id', default=-1, help='Specify what id to use for image')
@click.option('--snap', is_flag=True, help='If image is snapshot')
@click.option('--clone', is_flag=True, help='If image is provision clone')
@click.option('--public', is_flag=True, help='If image is public')
def add_image(project, img, id, snap, clone, public):
    with Database() as db:
        pid = db.project.fetch_id_with_name(project)
        if id == -1:
            db.image.insert(img, pid, public, snap, clone)
        else:
            db.image.insert(img, pid, public, snap, clone, id=id)
    click.echo("Success")


@db.command(name='ls', help='Lists All Images')
def list_all_images():
    with Database() as db:
        images = db.image.fetch_all_images()
        table = PrettyTable(
            field_names=["Id", "Name", "Project Name", "Is Public",
                         "Is Snapshot",
                         "Is Provision Clone"])
        for image in images:
            table.add_row(image)
    click.echo(table.get_string())


@cli.command(name='import',
             help='Clones an existing ceph image and makes it compatible with BMI')
@click.argument(constants.PROJECT_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.option('--snap', default="", help='Specifies what snapshot to import')
def convert_ceph_image(project, img, snap):
    if snap == "":
        with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
            with Database() as db:
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
    else:
        convert_ceph_snapshot(project, img, snap)
    click.echo("Success")


@cli.command(name='cp', help="Copy an existing image not clones")
@click.argument('src_project')
@click.argument('img1')
@click.argument('dest_project')
@click.argument('img2', default='')
def copy_image(src_project, img1, dest_project, img2):
    with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
        with Database() as db:
            pid = db.project.fetch_id_with_name(dest_project)
            db.image.copy_image(img1, src_project, img2, pid)
            if img2 != '':
                ceph_name = __get__ceph_image_name(img2, dest_project)
            else:
                ceph_name = __get__ceph_image_name(img1, dest_project)
            fs.clone(__get__ceph_image_name(img1, src_project),
                     constants.DEFAULT_SNAPSHOT_NAME, ceph_name)
            fs.snap_image(ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
            fs.snap_protect(ceph_name, constants.DEFAULT_SNAPSHOT_NAME)
    click.echo('Success')


@cli.command(name='mv', help='Move Image From Project to Another')
@click.argument('src_project')
@click.argument('img1')
@click.argument('dest_project')
@click.argument('img2', default='')
def move_image(src_project, img1, dest_project, img2):
    with Database() as db:
        pid = db.project.fetch_id_with_name(dest_project)
        db.image.move_image(src_project, img1, pid, img2)
    click.echo("Success")


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


def __get__ceph_image_name(name, project):
    with Database() as db:
        img_id = db.image.fetch_id_with_name_from_project(name, project)
        if img_id is None:
            logger.info("Raising Image Not Found Exception for %s", name)
            raise db_exceptions.ImageNotFoundException(name)

        return str(_cfg.uid) + "img" + str(img_id)


def convert_ceph_snapshot(project, img, snap_name):
    with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
        with Database() as db:
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


if __name__ == '__main__':
    cli()
