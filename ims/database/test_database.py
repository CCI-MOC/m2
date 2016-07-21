from unittest import TestCase

from ims.database.image import *
from ims.database.project import *


# Before running make sure no .db files are present in execution directory


# Tests for Project Class
class TestDatabase(TestCase):
    def test_database(self):
        # insert a project
        pr = ProjectRepository()
        pr.insert("project 1", "network 1")

        # insert another project
        pr.insert("project 2", "network 2")

        # check whether first project is present
        pid = pr.fetch_id_with_name("project 1")
        self.assertIsNotNone(pid)
        self.assertEqual(pid, 1)

        # check whether second project is present
        pid = pr.fetch_id_with_name("project 2")
        self.assertIsNotNone(pid)
        self.assertEqual(pid, 2)

        # verify that None is being returned for a project which doesnt exist
        pid = pr.fetch_id_with_name("project 3")
        self.assertIsNone(pid)

        # delete first project
        pr = ProjectRepository()
        pr.delete_with_name("project 1")

        # verify that it is gone
        pid = pr.fetch_id_with_name("project 1")
        self.assertIsNone(pid)

        # insert a image under second project
        imgr = ImageRepository()
        imgr.insert("image 1", 2)
        imgr.insert("image 1", 2)
        imgr.insert("image2", 2, True)
        # check that the image was inserted properly
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg, 1)

        # check that the image is not being returned from a different project name
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 1")
        qimg_list = imgr.fetch_names_with_public()
        qimg_names = imgr.fetch_names_from_project("project 2")
        self.assertIsNotNone(qimg_list)
        self.assertEqual(qimg_list[0]['image_name'], "image2")
        self.assertIsNone(qimg)
        self.assertIsNotNone(qimg_names)
        self.assertEqual(qimg_names.__len__(), 3)
        self.assertEqual(qimg_names[0], "image 1")

        # delete the inserted image
        imgr = ImageRepository()
        imgr.delete_with_name_from_project("image 1", "project 2")

        # checking that it is deleted
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 2")
        self.assertIsNone(qimg)

        # testing on delete cascade
        # Also brings the db to intial state
        pr = ProjectRepository()
        pr.delete_with_name("project 2")

        qp = pr.fetch_id_with_name("project 2")
        self.assertIsNone(qp)
