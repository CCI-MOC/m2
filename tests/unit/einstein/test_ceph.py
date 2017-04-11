import time
import unittest
import pytest
import subprocess
import ims.common.config as config

config.load()

import rados
import rbd
import ims.common.constants as constants
import ims.einstein.ceph as Ceph
from ims.database.database import Database
from ims.einstein.operations import BMI
import ims.exception.file_system_exceptions as file_system_exceptions
from ims.common.log import trace
from pytest import set_trace as bp
import logging

_cfg = config.get()

PROJECT = _cfg.tests.project
NETWORK = _cfg.tests.network

EXIST_IMG_NAME = _cfg.tests.exist_img_name
NEW_SNAP_NAME = _cfg.tests.new_snap_name
NOT_EXIST_IMG_NAME = _cfg.tests.not_exist_img_name
NOT_EXIST_SNAP_NAME = _cfg.tests.not_exist_snap_name

HIL_CALL_TIMEOUT = 5  # constants.HIL_CALL_TIMEOUT

POOL = _cfg.fs.pool
# test image
CEPH_IMG = "BMI_TEST_CEPH"
# test image size
CEPH_IMG_SIZE = 1024
# test snap_image
CEPH_EXISTING_IMG = "bmi_ci.img"
CEPH_SNAP_IMG = "BMI_TEST_CEPH_SNAP"
# test write
TEST_DATA = 'bmi' * 10
OFFSET = 0
# test clone
CEPH_CHILD_IMG = "BMI_TEST_CEPH_CHILD_IMAGE"


class TestListImages(unittest.TestCase):
    """
    Test list images
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        imgs = self.fs.list_images()
        command = "echo {0} | sudo -S rbd --keyring {1} --id {2} ls " \
                  "{3}".format(self.fs.password, self.fs.keyring,
                               self.fs.rid, self.fs.pool)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE)
        output, err = p.communicate()
        rbd_imgs = output.split()
        self.assertListEqual(imgs, rbd_imgs)
        time.sleep(HIL_CALL_TIMEOUT)

    def tearDown(self):
        print('In tearDown()')
        time.sleep(HIL_CALL_TIMEOUT)


class TestCreateImage(unittest.TestCase):
    """
    Test create image
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        imgs = self.fs.list_images()
        self.assertIn(CEPH_IMG, imgs)

    def tearDown(self):
        self.fs.remove(CEPH_IMG)
        time.sleep(HIL_CALL_TIMEOUT)


class TestRemoveImage(unittest.TestCase):
    """
    Test remove image and remove snapshot
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        self.fs.snap_image(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertRaises(file_system_exceptions.ImageHasSnapshotException,
                          self.fs.remove, CEPH_IMG)
        removess = self.fs.remove_snapshot(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(removess)
        remove = self.fs.remove(CEPH_IMG)
        self.assertTrue(remove)
        imgs = self.fs.list_images()
        self.assertNotIn(CEPH_IMG, imgs)

    def tearDown(self):
        pass


class TestClone(unittest.TestCase):
    """
    Clone image
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        # create image with format 2 which supports layering
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE, False, 1)
        self.fs.snap_image(CEPH_IMG, CEPH_SNAP_IMG)
        protectFlag = self.fs.snap_protect(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(protectFlag, "Failed to protect a snapshot!")
        cloneFlag = self.fs.clone(CEPH_IMG, CEPH_SNAP_IMG,
                                  CEPH_CHILD_IMG)
        self.assertTrue(cloneFlag, "Failed to clone image")
        children = self.fs.list_children(CEPH_IMG, CEPH_SNAP_IMG)
        children_imgs = [child[1] for child in children if child[0] == POOL]
        self.assertIn(CEPH_CHILD_IMG, children_imgs,
                      "Error, cannot find child image")
        parent_info = self.fs.get_parent_info(CEPH_CHILD_IMG)
        # parent_info = (pool name, image name, snapshot name)
        self.assertEqual(CEPH_IMG, parent_info[1])
        self.assertEqual(CEPH_SNAP_IMG, parent_info[2])

    def tearDown(self):
        self.fs.flatten(CEPH_CHILD_IMG)
        unprotectFlag = self.fs.snap_unprotect(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(unprotectFlag, "Failed to unprotect a snapshot")
        removeSnapFlag = self.fs.remove_snapshot(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(removeSnapFlag, "Failed to remove a snapshot")
        # remove parent image, note here remove order does not matter
        removeImg = self.fs.remove(CEPH_IMG)
        self.assertTrue(removeImg, "Failed to remove test parent image!")
        # remove child image
        removeChild = self.fs.remove(CEPH_CHILD_IMG)
        self.assertTrue(removeChild, "Failed to remove test child image clone \
                                       from parent image %s!" % CEPH_IMG)


class TestWrite(unittest.TestCase):
    """
    Write image
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        bytes_written = self.fs.write(CEPH_IMG, TEST_DATA, OFFSET)
        data_read = self.fs.read(CEPH_IMG, OFFSET, bytes_written)
        self.assertEqual(TEST_DATA, data_read)

    def tearDown(self):
        self.fs.remove(CEPH_IMG)
        time.sleep(HIL_CALL_TIMEOUT)


class TestSnapImage(unittest.TestCase):
    """
    create snapshot
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        imgs = self.fs.list_images()
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        snapFlag = self.fs.snap_image(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(snapFlag)
        snapList = self.fs.list_snapshots(CEPH_IMG)
        self.assertIn(CEPH_SNAP_IMG, snapList)
        self.assertNotIn(NOT_EXIST_SNAP_NAME, snapList)

    def tearDown(self):
        self.fs.remove_snapshot(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.remove(CEPH_IMG)


@unittest.skip("removeSnapShot class skipping")
class TestListSnapshot(unittest.TestCase):
    """
    List Snapshot
    """
    @unittest.skip("removeSnapShot class skipping")
    def setUp(self):
        pass

    def runTest(self):
        pass

    def tearDown(self):
        pass


@unittest.skip("removeSnapShot class skipping")
class TestRemoveSnapshot(unittest.TestCase):
    """
    Remove snapshot
    """
    @trace
    def setUp(self):
        pass

    def runTest(self):
        pass

    def tearDown(self):
        pass


class TestGetImage(unittest.TestCase):
    """
    Get image
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        good_img = self.fs.get_image(EXIST_IMG_NAME)
        self.assertEqual(good_img.name, EXIST_IMG_NAME)
        with self.assertRaises(file_system_exceptions.ImageNotFoundException):
            bad_img = self.fs.get_image(NOT_EXIST_IMG_NAME)

    def tearDown(self):
        pass


class TestMap(unittest.TestCase):
    """
    Test Map
    """
    @trace
    def setUp(self):
        self.fs = Ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        time.sleep(HIL_CALL_TIMEOUT)

    def runTest(self):
        device = self.fs.map(EXIST_IMG_NAME)
        mapped_info = self.fs.showmapped()
        self.assertIsNotNone(mapped_info[EXIST_IMG_NAME])

    def tearDown(self):
        mapped_info = self.fs.showmapped()
        snap_device = mapped_info[EXIST_IMG_NAME]
        self.fs.unmap(snap_device)
        mapped_info = self.fs.showmapped()
        self.assertEqual(len(mapped_info), 0)
