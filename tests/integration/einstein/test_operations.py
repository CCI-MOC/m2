# Tests the calls in einstein/operations.py

import time
import unittest
from unittest import TestCase

import ims.common.config as config

config.load()

import ims.common.constants as constants
import ims.einstein.ceph as ceph
from ims.common.log import trace
from ims.database.database import Database
from ims.einstein.operations import BMI

_cfg = config.get()

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


class TestProvision(TestCase):
    """ Imports an image and calls provision """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        response = self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                           NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestDeprovision(TestCase):
    """
    Same as above, but calls deprovision in the test (Test is same as previous)
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)


class TestCreateSnapshot(TestCase):
    """
    Provisions an imported image and creates snapshot
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.create_snapshot(NODE_NAME, NEW_SNAP_NAME)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

        snaps = self.db.image.fetch_snapshots_from_project(PROJECT)
        has_image = False
        for snapshot in snaps:
            if NEW_SNAP_NAME == snapshot[0]:
                has_image = True
        self.assertTrue(has_image)

        img_id = self.good_bmi.get_ceph_image_name_from_project(NEW_SNAP_NAME,
                                                                PROJECT)
        self.good_bmi.fs.get_image(img_id)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestListSnapshots(TestCase):
    """
    Creates snapshot like previous and calls list snapshots
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

        self.good_bmi.create_snapshot(NODE_NAME, NEW_SNAP_NAME)

    def runTest(self):
        response = self.good_bmi.list_snapshots()
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        self.assertEqual(response[constants.RETURN_VALUE_KEY][0][0],
                         NEW_SNAP_NAME)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


@unittest.skip("Same as Remove Image")
class TestRemoveSnapshot(TestCase):
    """
    Snapshot is also an image in bmi, so no need to test for now
    """

    def setUp(self):
        pass

    def runTest(self):
        pass

    def tearDown(self):
        pass


class TestListImages(TestCase):
    """
    Imports an image and calls list image
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        response = self.good_bmi.list_images()
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        self.assertEqual(response[constants.RETURN_VALUE_KEY],
                         [EXIST_IMG_NAME])

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestRemoveImage(TestCase):
    """
    Imports an image and calls remove image
    """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def runTest(self):
        response = self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
