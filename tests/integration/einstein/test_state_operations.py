import unittest
from unittest import TestCase

import ims.common.config as config

config.load()

import ims.common.constants as constants
from ims.common.log import trace
from ims.database.database import Database
from ims.einstein.operations import BMI
from ims.einstein.hil import HIL
from ims.einstein.ceph import RBD
from ims.einstein.iscsi.tgt import TGT

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


class TestProvisionHILAttached(TestCase):
    """ Tries Provisioning with node already attached """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.hil = HIL(base_url=_cfg.net_isolator.url,
                       usr=CORRECT_HIL_USERNAME,
                       passwd=CORRECT_HIL_PASSWORD)

        self.hil.attach_node_to_project_network(NODE_NAME, NETWORK, NIC)
        self.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                           NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)
        self.hil.wait(NODE_NAME, NETWORK, NIC)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestProvisionDBInserted(TestCase):
    """ Tries provisioning with node attached and db updated """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.hil.attach_node_to_project_network(NODE_NAME, NETWORK,
                                                         NIC)
        self.db.image.insert(NODE_NAME, 1, 1)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

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


class TestProvisionDBWrongParent(TestCase):
    """ Similar like above, but the row has a wrong parent """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.hil.attach_node_to_project_network(NODE_NAME, NETWORK,
                                                         NIC)
        self.db.image.insert(EXIST_IMG_NAME + "2", 1)
        self.db.image.insert(NODE_NAME, 1, 2)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                           NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 500)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestProvisionCloneDone(TestCase):
    """ Tries provisioning after cloning is also done """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.hil.attach_node_to_project_network(NODE_NAME, NETWORK,
                                                         NIC)
        self.db.image.insert(NODE_NAME, 1, 1)
        with RBD(_cfg.fs, _cfg.iscsi.password) as fs:
            fs.clone(_cfg.bmi.uid + "img1", constants.DEFAULT_SNAPSHOT_NAME,
                     _cfg.bmi.uid + "img2")
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

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


class TestProvisionCloneWrongParent(TestCase):
    """ Similar like above, but clone has a different parent """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)
        self.good_bmi.copy_image(EXIST_IMG_NAME, PROJECT, EXIST_IMG_NAME + "2")

        self.good_bmi.hil.attach_node_to_project_network(NODE_NAME, NETWORK,
                                                         NIC)
        self.db.image.insert(NODE_NAME, 1, 1)
        self.good_bmi.fs.clone(_cfg.bmi.uid + "img2",
                               constants.DEFAULT_SNAPSHOT_NAME,
                               _cfg.bmi.uid + "img3")
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK,
                                           NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 500)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def tearDown(self):
        self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.good_bmi.remove_image(EXIST_IMG_NAME + "2")
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestProvisionISCSIDone(TestCase):
    """ Tries provisioning after TGT target is also created """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.hil.attach_node_to_project_network(NODE_NAME, NETWORK,
                                                         NIC)
        self.db.image.insert(NODE_NAME, 1, 1)

        self.good_bmi.fs.clone(_cfg.bmi.uid + "img1",
                               constants.DEFAULT_SNAPSHOT_NAME,
                               _cfg.bmi.uid + "img2")
        self.good_bmi.iscsi.add_target(_cfg.bmi.uid + "img2")
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

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


class TestDeprovisionHILDetached(TestCase):
    """ Tries Deprovisioning after node is detached """
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)
        self.good_bmi.hil.detach_node_from_project_network(NODE_NAME, NETWORK,
                                                           NIC)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)

    def runTest(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestDeprovisionDBDeleted(TestCase):
    """ Tries Deprovisioning after db is deleted """
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.db.image.delete_with_name_from_project(NODE_NAME, PROJECT)
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 404)

    def tearDown(self):
        self.good_bmi.iscsi.remove_target(_cfg.bmi.uid + "img2")
        self.good_bmi.fs.remove(_cfg.bmi.uid + "img2")
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestDeprovisionISCSIDeleted(TestCase):
    """ Tries Deprovisioning after target is removed """
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.iscsi.remove_target(_cfg.bmi.uid + "img2")
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.good_bmi.remove_image(EXIST_IMG_NAME)
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)


class TestDeprovisionCephDeleted(TestCase):
    """ Tries Deprovisioning after clone is removed """
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert(PROJECT, NETWORK)

        self.good_bmi = BMI(CORRECT_HIL_USERNAME, CORRECT_HIL_PASSWORD,
                            PROJECT)
        self.good_bmi.import_ceph_image(EXIST_IMG_NAME)

        self.good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, NETWORK, NIC)
        self.good_bmi.iscsi.remove_target(_cfg.bmi.uid + "img2")
        self.good_bmi.fs.remove(_cfg.bmi.uid + "img2")
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC)

    def runTest(self):
        response = self.good_bmi.deprovision(NODE_NAME, NETWORK, NIC)
        self.assertEqual(response[constants.STATUS_CODE_KEY], 200)

    def tearDown(self):
        self.db.project.delete_with_name(PROJECT)
        self.db.close()
        self.good_bmi.shutdown()
        self.good_bmi.hil.wait(NODE_NAME, NETWORK, NIC, False)
