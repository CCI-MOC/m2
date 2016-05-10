from unittest import TestCase
from database import Database
from project import Project
from image import Image

# Before running make sure no .db files are present in execution directory

# the database object which will be used in all tests
db = Database()

# Tests for Project Class
class TestProject(TestCase):

    # the test for insert
    # insert two rows and verify with fetch
    # also verify for row which is not there (testing fetch also)
    def test_insert(self):
        p1 = Project(db)

        p1.name = "project 1"
        p1.provision_network = "network 1"
        p1.insert()

        p2 = Project(db)
        p2.name = "project 2"
        p2.provision_network = "network 2"
        p2.insert()

        qp = p1.fetch_with_name("project 1")
        self.assertIsNotNone(qp)
        self.assertEqual(qp.name, "project 1")

        qp = p2.fetch_with_name("project 2")
        self.assertIsNotNone(qp)
        self.assertEqual(qp.name, "project 2")

        qp = p1.fetch_with_name("project 3")
        self.assertIsNone(qp)

    # the test for delete
    # delete the inserted row
    # check if it is gone
    def test_delete_with_name(self):
        p = Project(db)
        p.delete_with_name("project 1")

        qp = p.fetch_with_name("project 1")
        self.assertIsNone(qp)

# Tests for Image Class
class TestImage(TestCase):

    # test for insert
    # insert image for existing project
    # check whether inserted properly
    # check whether image is not being returned if project changed (testing fetch)
    def test_insert(self):
        img = Image(db)
        img.name = "image 1"
        img.project_id = 2
        img.insert()

        qimg = img.fetch_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg.__len__(), 1)
        self.assertEqual(qimg[0].name, "image 1")
        self.assertEqual(qimg[0].project.name, "project 2")

        qimg = img.fetch_with_name_from_project("image 1", "project 1")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg.__len__(), 0)

    # test for delete
    # delete existing row
    # check whether row is gone
    def test_delete_with_name(self):
        img = Image(db)
        img.delete_with_name("image 1")

        qimg = img.fetch_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)
