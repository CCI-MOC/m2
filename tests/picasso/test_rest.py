import base64
import time
import unittest
import requests
from unittest import TestCase

import ims.common.constants as constants
import ims.einstein.ceph as ceph
from ims.database import *
from ims.einstein.operations import BMI

_cfg = config.get()

url = "http://192.168.122.34:7000/"

CORRECT_HAAS_USERNAME = "haasadmin"
CORRECT_HAAS_PASSWORD = "admin1234"
INCORRECT_HAAS_PASSWORD = "admin123##"

NODE_NAME = "cisco-27"
CHANNEL = "vlan/native"
NIC = "enp130s0f0"

PROJECT = "bmi_infra"
NETWORK = "bmi-provision"

EXIST_IMG_NAME = "bmi_ci.img"
NEW_SNAP_NAME = 'test_snap'
NOT_EXIST_IMG_NAME = "i12"
NOT_EXIST_SNAP_NAME = "hello"

credentials = (
    base64.b64encode(CORRECT_HAAS_USERNAME + ":" + CORRECT_HAAS_PASSWORD),
    PROJECT,)


def __get_ceph_image_name(name, project):
    with Database() as db:
        img_id = db.image.fetch_id_with_name_from_project(name, project)
        if img_id is None:
            logger.info("Raising Image Not Found Exception for %s", name)
            raise db_exceptions.ImageNotFoundException(name)

        return str(_cfg.uid) + "img" + str(img_id)


class TestProvision(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.IMAGE_NAME_PARAMETER: EXIST_IMG_NAME,
                constants.NETWORK_PARAMETER: NETWORK,
                constants.CHANNEL_PARAMETER: CHANNEL,
                constants.NIC_PARAMETER: NIC}
        res = requests.put(url + "provision/", data=data,
                           auth=(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        self.assertEqual(res.status_code, 200)
        time.sleep(30)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(30)


class TestDeprovision(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                CHANNEL, NIC)
        time.sleep(30)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.NETWORK_PARAMETER: NETWORK,
                constants.NIC_PARAMETER: NIC}
        res = requests.put(url + "deprovision/", data=data,
                           auth=(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        self.assertEqual(res.status_code, 200)
        time.sleep(30)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestCreateSnapshot(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                CHANNEL, NIC)
        time.sleep(30)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.NODE_NAME_PARAMETER: NODE_NAME,
                constants.SNAP_NAME_PARAMETER: NEW_SNAP_NAME}
        res = requests.put(url + "create_snapshot/", data=data,
                           auth=(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        self.assertEqual(res.status_code, 200)

        snaps = self.db.image.fetch_snapshots_from_project(PROJECT)
        yes = NEW_SNAP_NAME in snaps
        self.assertTrue(yes)

        with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
            global __get_ceph_image_name
            img_id = __get_ceph_image_name(NEW_SNAP_NAME, PROJECT)
            fs.get_image(img_id)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(30)


class TestListSnapshots(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)
        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                CHANNEL, NIC)
        time.sleep(30)

        self.good_bmi.create_snapshot(NODE_NAME, NEW_SNAP_NAME)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT}
        res = requests.post(url + "list_snapshots/", data=data,
                            auth=(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        self.assertEqual(res.status_code, 200)
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js[0], NEW_SNAP_NAME)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(NEW_SNAP_NAME)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        time.sleep(30)


@unittest.skip('Same as Remove Image')
class TestRemoveSnapshot(TestCase):
    def setUp(self):
        pass

    def test_run(self):
        pass

    def tearDown(self):
        pass


class TestListImages(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT}
        res = requests.post(url + "list_images/", data=data,
                            auth=(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        print res.content
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js[0], EXIST_IMG_NAME)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


class TestRemoveImage(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)
        import_test(EXIST_IMG_NAME)

        self.good_bmi = BMI(credentials)

    def test_run(self):
        data = {constants.PROJECT_PARAMETER: PROJECT,
                constants.IMAGE_NAME_PARAMETER: NEW_SNAP_NAME}
        res = requests.delete(url + "remove_image/", data=data, auth=(
            CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD))
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()


def import_test(img):
    with ceph.RBD(_cfg.fs[constants.CEPH_CONFIG_SECTION_NAME]) as fs:
        with Database() as db:
            pid = db.project.fetch_id_with_name(PROJECT)
            ceph_img_name = str(img)

            fs.snap_image(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            fs.snap_protect(ceph_img_name, constants.DEFAULT_SNAPSHOT_NAME)
            db.image.insert(ceph_img_name, pid)
            snap_ceph_name = __get_ceph_image_name(ceph_img_name, PROJECT)
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
