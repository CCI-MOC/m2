import time
import unittest
import subprocess
from ims.common import config

config.load()

import rados
import rbd
from ims.common import shell
from ims.common import constants
from ims.einstein import ceph
from ims.einstein.operations import BMI
from ims.exception import file_system_exceptions
from ims.common.log import trace
import logging

_cfg = config.get()

POOL = _cfg.fs.pool
CEPH_IMG = "BMI_TEST_CEPH"
TEST_NOT_EXIST_IMG_NAME = "BMI_TEST_IMG_NOT_FOUND"
CEPH_IMG_SIZE = 1024
INDEX_OUTSIDE_THE_IMAGE = CEPH_IMG_SIZE + 1
CEPH_SNAP_IMG = "BMI_TEST_CEPH_SNAP"
TEST_DATA = 'bmi' * 10
OFFSET = 0
CEPH_CHILD_IMG = "BMI_TEST_CEPH_CHILD_IMAGE"


class TestCreateImage(unittest.TestCase):
    """ Test create image """
    @trace
    def setUp(self):
        self.fs = ceph.RBD(_cfg.fs, _cfg.iscsi.password)

    def runTest(self):
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        self.assertIn(CEPH_IMG, self.fs.list_images())

    def tearDown(self):
        self.fs.remove(CEPH_IMG)


class TestRemoveImage(unittest.TestCase):
    """ Test remove image """
    @trace
    def setUp(self):
        self.fs = ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)

    def runTest(self):
        self.fs.remove(CEPH_IMG)
        self.assertNotIn(CEPH_IMG, self.fs.list_images())


class TestImage(unittest.TestCase):
    """ Test image operations """
    @trace
    def setUp(self):
        self.fs = ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)

    def test_get_image(self):
        """ Test whether the image with given name is found or not """
        good_img = self.fs.get_image(CEPH_IMG)
        self.assertEqual(good_img.name, CEPH_IMG)

    def test_image_not_found_exception(self):
        """
        This error will be raised when image is not found
        """
        with self.assertRaises(file_system_exceptions.ImageNotFoundException):
            bad_img = self.fs.get_image(TEST_NOT_EXIST_IMG_NAME)

    def test_list_images(self):
        """ Test list mages """
        self.assertIn(CEPH_IMG, self.fs.list_images())

    def test_argument_out_of_range_exception_in_read(self):
        """
        This error will be raised in read function if part of the range
        specified is outside the image
        """
        self.assertRaises(file_system_exceptions.ArgumentsOutOfRangeException,
                          self.fs.read, CEPH_IMG, INDEX_OUTSIDE_THE_IMAGE,
                          len(TEST_DATA))

    def test_argument_out_of_range_exception_in_write(self):
        """
        This error will be raised in write function if part of the write would
        fall outside the image
        """
        self.assertRaises(file_system_exceptions.ArgumentsOutOfRangeException,
                          self.fs.write, CEPH_IMG, TEST_DATA,
                          INDEX_OUTSIDE_THE_IMAGE)

    def test_write_and_read(self):
        """ Test writting data into image """
        bytes_written = self.fs.write(CEPH_IMG, TEST_DATA, OFFSET)
        data_read = self.fs.read(CEPH_IMG, OFFSET, bytes_written)
        self.assertEqual(TEST_DATA, data_read)

    def tearDown(self):
        self.fs.remove(CEPH_IMG)


class TestSnapshot(unittest.TestCase):
    """ Test snapshot operations """
    @trace
    def setUp(self):
        self.fs = ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        self.fs.snap_image(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.snap_protect(CEPH_IMG, CEPH_SNAP_IMG)

    def test_list_snapshots(self):
        """ Test if list_snapshot function lists all snapshots of a image """
        self.assertIn(CEPH_SNAP_IMG, self.fs.list_snapshots(CEPH_IMG))

    def test_image_exist_exception(self):
        """ This error will be raised if snap image already exists """
        self.assertRaises(file_system_exceptions.ImageExistsException,
                          self.fs.snap_image, CEPH_IMG, CEPH_SNAP_IMG)

    def test_image_has_snapshot_exception(self):
        """
        This error will be raised if user removes a image which has snapshot
        """
        self.assertRaises(file_system_exceptions.ImageHasSnapshotException,
                          self.fs.remove, CEPH_IMG)

    def test_snapshot_busy_exception(self):
        """ This error will be raised if user removes a protected snapshot """
        self.assertRaises(file_system_exceptions.SnapshotBusyException,
                          self.fs.remove_snapshot, CEPH_IMG, CEPH_SNAP_IMG)

    def test_snap_protect(self):
        """
        Test snap_protect. If a snapshot is marked as protected,
        function is_snap_protected will return True
        """
        is_protected = self.fs.is_snap_protected(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertTrue(is_protected, "Failed to protect a snapshot!")

    def test_snap_unprotect(self):
        """
        Test snap_unprotect. If a snapshot is marked as unprotected,
        function is_snap_protected will return False
        """
        self.fs.snap_unprotect(CEPH_IMG, CEPH_SNAP_IMG)
        is_protected = self.fs.is_snap_protected(CEPH_IMG, CEPH_SNAP_IMG)
        self.assertFalse(is_protected, "Failed to unprotect a snapshot!")

    def tearDown(self):
        if self.fs.is_snap_protected(CEPH_IMG, CEPH_SNAP_IMG):
            self.fs.snap_unprotect(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.remove_snapshot(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.remove(CEPH_IMG)


class TestClone(unittest.TestCase):
    """ Test clone operations """
    @trace
    def setUp(self):
        self.fs = ceph.RBD(_cfg.fs, _cfg.iscsi.password)
        self.fs.create_image(CEPH_IMG, CEPH_IMG_SIZE)
        self.fs.snap_image(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.snap_protect(CEPH_IMG, CEPH_SNAP_IMG)

    def runTest(self):
        """ Test clone image, clone a parent rbd snapshot into a COW child """
        self.fs.clone(CEPH_IMG, CEPH_SNAP_IMG, CEPH_CHILD_IMG)
        children = self.fs.list_children(CEPH_IMG, CEPH_SNAP_IMG)
        children_imgs = [child[1] for child in children if child[0] == POOL]
        self.assertIn(CEPH_CHILD_IMG, children_imgs,
                      "Error, cannot find child image")
        parent_info = self.fs.get_parent_info(CEPH_CHILD_IMG)
        self.assertEqual(CEPH_IMG, parent_info[1])
        self.assertEqual(CEPH_SNAP_IMG, parent_info[2])

    def tearDown(self):
        self.fs.remove(CEPH_CHILD_IMG)
        self.fs.snap_unprotect(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.remove_snapshot(CEPH_IMG, CEPH_SNAP_IMG)
        self.fs.remove(CEPH_IMG)
