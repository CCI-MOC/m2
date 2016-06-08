import time
import unittest
from operations import *

CORRECT_HAAS_USERNAME = "haasadmin"
CORRECT_HAAS_PASSWORD = "admin1234"
INCORRECT_HAAS_PASSWORD = "admin123##"

NODE_NAME = "cisco-27"
CHANNEL = "vlan/native"
NIC = "enp130s0f0"

PROJECT = "bmi_infra"
NETWORK = "bmi-provision"

EXIST_IMG_NAME = "hadoopMaster.img"
EXIST_SNAP_NAME = "HadoopMasterGoldenImage"
NOT_EXIST_IMG_NAME = "i12"
NOT_EXIST_SNAP_NAME = "hello"

NEW_SNAP_NAME = "blblb1"  # for creating snapshot


class TestOperations(unittest.TestCase):
    def test_provision(self):
        good_bmi = BMI(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD)
        bad_bmi = BMI(CORRECT_HAAS_USERNAME, INCORRECT_HAAS_PASSWORD)

        # output = bad_bmi.provision(NODE_NAME, EXIST_IMG_NAME, EXIST_SNAP_NAME,
        #                            NETWORK)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.provision(NODE_NAME, NOT_EXIST_IMG_NAME,
                                    EXIST_SNAP_NAME, NETWORK,CHANNEL,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        time.sleep(30)

        output = good_bmi.detach_node(NODE_NAME, NETWORK,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 500)

        time.sleep(30)

        output = good_bmi.provision(NODE_NAME, EXIST_IMG_NAME,
                                    NOT_EXIST_SNAP_NAME, NETWORK,CHANNEL,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        time.sleep(30)

        output = good_bmi.detach_node(NODE_NAME, NETWORK,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 500)

        time.sleep(30)

        output = good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, EXIST_SNAP_NAME,
                                    NETWORK,CHANNEL,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)

        output = good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, EXIST_SNAP_NAME,
                                    NETWORK,CHANNEL,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 500)

        time.sleep(30)

        output = good_bmi.provision(NODE_NAME, EXIST_IMG_NAME, EXIST_SNAP_NAME,
                                    NETWORK,CHANNEL,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 500)

        # output = bad_bmi.detach_node(NODE_NAME, NETWORK)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.detach_node(NODE_NAME, NETWORK,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)

        output = good_bmi.detach_node(NODE_NAME, NETWORK,NIC)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 500)

    def test_create_snapshot(self):
        good_bmi = BMI(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD)
        bad_bmi = BMI(CORRECT_HAAS_USERNAME, INCORRECT_HAAS_PASSWORD)

        print "create snapshot"
        # output = bad_bmi.create_snapshot(PROJECT, NOT_EXIST_IMG_NAME,
        #                                  NEW_SNAP_NAME)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.create_snapshot(PROJECT,
                                          NOT_EXIST_IMG_NAME, NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        pr = ProjectRepository()
        pr.insert(PROJECT, NETWORK)

        output = good_bmi.create_snapshot(PROJECT,
                                          NOT_EXIST_IMG_NAME, NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        imgr = ImageRepository()
        imgr.insert(NOT_EXIST_IMG_NAME, 1)
        imgr.insert(EXIST_IMG_NAME, 1, id=2)

        output = good_bmi.create_snapshot(PROJECT,
                                          NOT_EXIST_IMG_NAME, NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        output = good_bmi.create_snapshot(PROJECT,
                                          EXIST_IMG_NAME, NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)

        pr.delete_with_name(PROJECT)

        print "list snapshots"
        # output = bad_bmi.list_snaps(PROJECT, NOT_EXIST_IMG_NAME)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.list_snaps(PROJECT, NOT_EXIST_IMG_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        pr = ProjectRepository()
        pr.insert(PROJECT, NETWORK, id=1)

        output = good_bmi.list_snaps(PROJECT, NOT_EXIST_IMG_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        imgr = ImageRepository()
        imgr.insert(NOT_EXIST_IMG_NAME, 1, id=1)
        imgr.insert(EXIST_IMG_NAME, 1, id=2)

        output = good_bmi.list_snaps(PROJECT, NOT_EXIST_IMG_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        output = good_bmi.list_snaps(PROJECT, EXIST_IMG_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)
        self.assertEqual(output[constants.RETURN_VALUE_KEY][-1], NEW_SNAP_NAME)

        output = good_bmi.create_snapshot(PROJECT, EXIST_IMG_NAME,
                                          NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 471)

        pr.delete_with_name(PROJECT)

        print "remove snapshots"
        # output = bad_bmi.remove_snaps(PROJECT, NOT_EXIST_IMG_NAME,
        #                               NEW_SNAP_NAME)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.remove_snaps(PROJECT, NOT_EXIST_IMG_NAME,
                                       NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        pr = ProjectRepository()
        pr.insert(PROJECT, NETWORK, id=1)

        output = good_bmi.remove_snaps(PROJECT,
                                       NOT_EXIST_IMG_NAME,
                                       NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        imgr = ImageRepository()
        imgr.insert(NOT_EXIST_IMG_NAME, 1, id=1)
        imgr.insert(EXIST_IMG_NAME, 1, id=2)

        output = good_bmi.remove_snaps(PROJECT,
                                       NOT_EXIST_IMG_NAME,
                                       NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        output = good_bmi.remove_snaps(PROJECT, EXIST_IMG_NAME,
                                       NEW_SNAP_NAME)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)

        pr.delete_with_name(PROJECT)

    def test_list_all_images(self):
        good_bmi = BMI(CORRECT_HAAS_USERNAME, CORRECT_HAAS_PASSWORD)
        bad_bmi = BMI(CORRECT_HAAS_USERNAME, INCORRECT_HAAS_PASSWORD)

        # output = bad_bmi.list_all_images(PROJECT)
        # print output
        # self.assertEqual(output[constants.STATUS_CODE_KEY], 401)

        output = good_bmi.list_all_images(PROJECT)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 404)

        pr = ProjectRepository()
        pr.insert(PROJECT, NETWORK)

        output = good_bmi.list_all_images(PROJECT)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)
        self.assertEqual(output[constants.RETURN_VALUE_KEY].__len__(), 0)
        self.assertEqual(output[constants.RETURN_VALUE_KEY], [])

        imgr = ImageRepository()
        imgr.insert(EXIST_IMG_NAME, 1)

        output = good_bmi.list_all_images(PROJECT)
        print output
        self.assertEqual(output[constants.STATUS_CODE_KEY], 200)
        self.assertEqual(output[constants.RETURN_VALUE_KEY].__len__(), 1)
        self.assertEqual(output[constants.RETURN_VALUE_KEY][0], EXIST_IMG_NAME)

        pr.delete_with_name(PROJECT)
