#!/usr/bin/python
import os

import click
import requests

import ims.common.config as config
import ims.common.constants as constants

config.load()

_cfg = config.get()

_url = "http://{0}:{1}/".format(_cfg.bind_ip, _cfg.bind_port)

_project = os.environ[constants.PROJECT_ENV_VARIABLE]
_username = os.environ[constants.HAAS_USERNAME_VARIABLE]
_password = os.environ[constants.HAAS_PASSWORD_VARIABLE]


@click.group()
def cli():
    pass


@click.command(
    help="Provisions a <NODE> with an <IMAGE> connected on <NIC> to <NETWORK> through <CHANNEL>")
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.IMAGE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.CHANNEL_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def provision(node, image, network, channel, nic):
    data = {constants.PROJECT_PARAMETER: _project,
            constants.NODE_NAME_PARAMETER: node,
            constants.IMAGE_NAME_PARAMETER: image,
            constants.NETWORK_PARAMETER: network,
            constants.CHANNEL_PARAMETER: channel,
            constants.NIC_PARAMETER: nic}
    res = requests.put(_url + "provision/", data=data,
                       auth=(_username, _password))
    print res.content


@click.command(help='Deprovision <NODE> from <NETWORK> connected on <NIC>')
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.NETWORK_PARAMETER)
@click.argument(constants.NIC_PARAMETER)
def deprovision(node, network, nic):
    pass


@click.command(help='Create Snapshot of <NODE> as <SNAP_NAME>')
@click.argument(constants.NODE_NAME_PARAMETER)
@click.argument(constants.SNAP_NAME_PARAMETER)
def create_snapshot(node, snap_name):
    pass


@click.command(help='List All Snapshots Stored')
def list_snapshots():
    pass


@click.command(help='Remove <IMAGE>')
@click.argument(constants.IMAGE_NAME_PARAMETER)
def remove_image(image):
    pass


@click.command(help='List All Images Stored')
def list_images():
    data = {constants.PROJECT_PARAMETER: _project}
    res = requests.post(_url + "list_images/", data=data,
                        auth=(_username, _password))
    print res.content


cli.add_command(provision)
cli.add_command(deprovision)
cli.add_command(create_snapshot)
cli.add_command(list_snapshots)
cli.add_command(remove_image)
cli.add_command(list_images)

if __name__ == '__main__':
    cli()
