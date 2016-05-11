from unittest import TestCase

from database import DatabaseConnection
from image import Image
from project import Project

# Before running make sure no .db files are present in execution directory

# the database object which will be used in all tests


# Tests for Project Class
class TestProject(TestCase):
    # the test for insert
    # insert two rows and verify with fetch
    # also verify for row which is not there (testing fetch also)
    def insert_test(self):
        # insert a project
        p1 = Project()
        p1.name = "project 1"
        p1.provision_network = "network 1"
        p1.insert()

        # insert another project
        p2 = Project()
        p2.name = "project 2"
        p2.provision_network = "network 2"
        p2.insert()

        # check whether first project is present
        qp = Project.fetch_with_name("project 1")
        self.assertIsNotNone(qp)
        self.assertEqual(qp.name, "project 1")

        # check whether second project is present
        qp = Project.fetch_with_name("project 2")
        self.assertIsNotNone(qp)
        self.assertEqual(qp.name, "project 2")

        # verify that None is being returned for a project which doesnt exist
        qp = Project.fetch_with_name("project 3")
        self.assertIsNone(qp)

    # the test for delete
    # delete the inserted row
    # check if it is gone
    def delete_with_name_test(self):
        # delete first project
        p = Project.fetch_with_name("project 1")
        p.delete()

        # verify that it is gone
        qp = Project.fetch_with_name("project 1")
        self.assertIsNone(qp)

    def test_project(self):
        self.insert_test()
        self.delete_with_name_test()


# Tests for Image Class
class TestImage(TestCase):
    # test for insert
    # insert image for existing project
    # check whether inserted properly
    # check whether image is not being returned if project changed (testing fetch)
    def insert_test(self):
        # insert a image under second project
        img = Image()
        img.name = "image 1"
        img.project_id = 2
        img.insert()

        # check that the image was inserted properly
        qimg = Image.fetch_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg.__len__(), 1)
        self.assertEqual(qimg[0].name, "image 1")
        self.assertEqual(qimg[0].project.name, "project 2")

        # check that the image is not being returned from a different project name
        qimg = Image.fetch_with_name_from_project("image 1", "project 1")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg.__len__(), 0)

    # test for delete
    # delete existing row
    # check whether row is gone
    def delete_with_name_test(self):
        # delete the inserted image
        imges = Image.fetch_with_name_from_project("image 1", "project 2")
        imges[0].delete()

        # checking that it is deleted
        qimg = Image.fetch_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)

    def test_image(self):
        self.insert_test()
        self.delete_with_name_test()
