import time
import unittest
from unittest import TestCase

import ims.common.constants as constants
import ims.einstein.ceph as ceph
from ims.einstein.operations import BMI

_cfg = config.get()

CORRECT_HIL_USERNAME = "haasadmin"
CORRECT_HIL_PASSWORD = "admin1234"
INCORRECT_HIL_PASSWORD = "admin123##"

NODE_NAME = "cisco-24"
NIC = "enp130s0f0"

PROJECT = "bmi_infra"
NETWORK = "bmi-provision"

EXIST_IMG_NAME = "bmi_ci.img"
NEW_SNAP_NAME = 'test_snap'
NOT_EXIST_IMG_NAME = "i12"
NOT_EXIST_SNAP_NAME = "hello"


class TestProvision(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def test_run(self):
        response = self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                           NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(constants.HIL_CALL_TIMEOUT)


class TestDeprovision(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def test_run(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestCreateSnapshot(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        time.sleep(constants.HIL_CALL_TIMEOUT)

    def test_run(self):
        response = self.good_bmi.create_snapshot(NODE_NAME, NEW_SNAP_NAME)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

        snaps = self.db.image.fetch_snapshots_from_project(PROJECT)
        has_image = False
        for snapshot in snaps:
            if NEW_SNAP_NAME == snapshot[0]:
                has_image = True
        self.assertTrue(has_image)

        with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME],
                      _cfg.iscsi_update_password) as fs:
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

    def test_run(self):
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
        time.sleep(constants.HIL_CALL_TIMEOUT)


@unittest.skip("Same as Remove Image")
class TestRemoveSnapshot(TestCase):
    def setUp(self):
        pass

    def test_run(self):
        pass

    def tearDown(self):
        pass


class TestListImages(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def test_run(self):
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
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

    def test_run(self):
        response = self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
