from unittest import TestCase

from repositories.image_repository import ImageRepository
from repositories.project_repository import ProjectRepository


# Before running make sure no .db files are present in execution directory


# Tests for Project Class
class TestDatabase(TestCase):
    # should not actually be called
    # the test for insert
    # insert two rows and verify with fetch
    # also verify for row which is not there (testing fetch also)
    def insert_project_test(self):
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

    # should not actually be called
    # the test for delete
    # delete the inserted row
    # check if it is gone
    def delete_with_name_project_test(self):
        # delete first project
        pr = ProjectRepository()
        pr.delete_with_name("project 1")

        # verify that it is gone
        pid = pr.fetch_id_with_name("project 1")
        self.assertIsNone(pid)

    # should not be called
    # runs the project test case
    def project_test(self):
        self.insert_project_test()
        self.delete_with_name_project_test()

    # should not be called
    # test for insert
    # insert image for existing project
    # check whether inserted properly
    # check whether image is not being returned if project changed (testing fetch)
    def insert_image_test(self):
        # insert a image under second project
        imgr = ImageRepository()
        imgr.insert("image 1", 2)
        imgr.insert("image1", 2)
        imgr.insert("image2", 2, True)
        # check that the image was inserted properly
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 2")
        self.assertIsNotNone(qimg)
        self.assertEqual(qimg, 1)

        # check that the image is not being returned from a different project name
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 1")
        qimg_list = imgr.fetch_name_with_public()
        self.assertIsNotNone(qimg_list)
        self.assertEqual(qimg_list[0]['image_name'], "image2")
        self.assertIsNone(qimg)

    # should not be called
    # test for delete
    # delete existing row
    # check whether row is gone
    def delete_with_name_image_test(self):
        # delete the inserted image
        imgr = ImageRepository()
        imgr.delete_with_name_from_project("image 1", "project 2")

        # checking that it is deleted
        qimg = imgr.fetch_id_with_name_from_project("image 1", "project 2")
        self.assertIsNone(qimg)

    # should not be called
    # runs the image test case
    def image_test(self):
        self.insert_image_test()
        self.delete_with_name_image_test()

    # The actual test that should be called
    # written for ordering of tests
    def test_database(self):
        self.project_test()
        self.image_test()
