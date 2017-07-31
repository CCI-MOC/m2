# Tests the rest calls in picasso/rest.py
# TODO Make a TestLib and add common setup and teardown functions

import time
import unittest
from unittest import TestCase

import requests
from threading import Thread
import ims.common.config as config

config.load()

import ims.picasso.rest as rest
from ims.rpc.server.name_server import start_name_server
from ims.rpc.server.rpc_server import start_rpc_server
import ims.common.constants as constants
import ims.einstein.ceph as ceph
from ims.common.log import trace
from ims.database.database import Database
from ims.einstein.operations import BMI

_cfg = config.get()

PICASSO_URL = _cfg.tests.picasso_url

CORRECT_HIL_USERNAME = _cfg.tests.correct_hil_username
CORRECT_HIL_PASSWORD = _cfg.tests.correct_hil_password
INCORRECT_HIL_PASSWORD = _cfg.tests.incorrect_hil_password

NODE_NAME = _cfg.tests.node_name
NIC = _cfg.tests.nic

PROJECT = _cfg.tests.project
NETWORK = _cfg.tests.network

EXIST_IMG_NAME = _cfg.tests.exist_img_name
NEW_SNAP_NAME = _cfg.tests.new_snap_name
NOT_EXIST_IMG_NAME = _cfg.tests.not_exist_img_name
NOT_EXIST_SNAP_NAME = _cfg.tests.not_exist_snap_name

# The Coverage Issue for these tests was that no coverage data was
# being generated for the server processes.

# To solve this I made the server processes to run as threads as
# coverage.py covers threads by default.

# The next issue was stopping these threads when the tests were done.
# To solve this I created a child thread that starts the server threads
# as daemon threads and checks a global variable.

# When the global variable is true the thread exits and the server threads
# die as they are daemon threads.

# This successfully results in flushing of coverage data.
threads = []
stop_services = False


def start_services():
    global threads, stop_services
    stop_services = False
    threads = [Thread(target=start_name_server),
               Thread(target=start_rpc_server),
               Thread(target=rest.start)]
    for t in threads:
        t.daemon = True
        t.start()

    while not stop_services:
        time.sleep(0)


def setUpModule():
    t = Thread(target=start_services)
    t.start()


def tearDownModule():
    global stop_services
    stop_services = True


class TestProvision(TestCase):
    """
    Tests Rest Provision call by importing an image and calling provision
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.IMAGE_NAME_PARAMETER: EXIST_IMG_NAME,
                constants.NETWORK_PARAMETER: NETWORK,
                constants.NIC_PARAMETER: NIC}
        res = requests.put(PICASSO_URL + "provision/", data=data,
                           auth=(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD))
        self.assertEqual(res.status_code, 200)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(constants.HIL_CALL_TIMEOUT)


class TestDeprovision(TestCase):
    """
    Tests Rest Deprovision call by doing previous steps and calling deprovision
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.NETWORK_PARAMETER: NETWORK,
                constants.NIC_PARAMETER: NIC}
        res = requests.delete(PICASSO_URL + "deprovision/", data=data,
                              auth=(
                                  CORRECT_HIL_USERNAME,
                                  CORRECT_HIL_PASSWORD))
        self.assertEqual(res.status_code, 200)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestCreateSnapshot(TestCase):
    """
    Calls provision like TestProvision then creates a snapshot using rest call
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.SNAP_NAME_PARAMETER: NEW_SNAP_NAME}
        res = requests.put(PICASSO_URL + "create_snapshot/", data=data,
                           auth=(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD))
        self.assertEqual(res.status_code, 200)

        snaps = self.db.image.fetch_snapshots_from_project(PROJECT)
        has_image = False
        for snapshot in snaps:
            if NEW_SNAP_NAME == snapshot[0]:
                has_image = True
        self.assertTrue(has_image)

        with ceph.RBD(_cfg.fs,
                      _cfg.iscsi.password) as fs:
            img_id = self.good_bmi.get_ceph_image_name_from_project(
                NEW_SNAP_NAME, PROJECT)
            fs.get_image(img_id)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(constants.HIL_CALL_TIMEOUT)


class TestListSnapshots(TestCase):
    """
    Does the same steps as previous test and calls list snapshots rest call
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        time.sleep(constants.HIL_CALL_TIMEOUT)

        self.good_bmi.create_snapshot(NODE_NAME, NEW_SNAP_NAME)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT}
        res = requests.post(PICASSO_URL + "list_snapshots/", data=data,
                            auth=(CORRECT_HIL_USERNAME,
                                  CORRECT_HIL_PASSWORD))
        self.assertEqual(res.status_code, 200)
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js[0][0], NEW_SNAP_NAME)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(constants.HIL_CALL_TIMEOUT)


@unittest.skip('Same as Remove Image')
class TestRemoveSnapshot(TestCase):
    """
    This is because snapshot is also an image in out terms currently
    """

    def setUp(self):
        pass

    def runTest(self):
        pass

    def tearDown(self):
        pass


class TestListImages(TestCase):
    """
    Imports an import image and calls the list images rest call
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT}
        res = requests.post(PICASSO_URL + "list_images/", data=data,
                            auth=(CORRECT_HIL_USERNAME,
                                  CORRECT_HIL_PASSWORD))
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js[0], EXIST_IMG_NAME)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestRemoveImage(TestCase):
    """
    Imports an Image and calls the remove image rest call
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.IMAGE_NAME_PARAMETER: EXIST_IMG_NAME}
        res = requests.delete(PICASSO_URL + "remove_image/", data=data, auth=(
            CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD))
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
