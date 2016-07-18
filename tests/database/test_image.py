import unittest
from unittest import TestCase

from ims.database import *


class TestInsert(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def test_run(self):
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_public=True)
        self.db.image.insert('image 3', 1, is_provision_clone=True)
        self.db.image.insert('image 4', 1, is_snapshot=True)

        images = self.db.image.fetch_images_from_project('project 1')
        yes = 'image 1' in images and 'image 2' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_clones_from_project('project 1')
        yes = 'image 3' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_snapshots_from_project('project 1')
        yes = 'image 4' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_names_with_public()
        yes = 'image 2' in images
        self.assertTrue(yes)

    def tearDown(self):
        self.db.image.delete_with_name_from_project('image 1', 'project 1')
        self.db.image.delete_with_name_from_project('image 2', 'project 1')
        self.db.image.delete_with_name_from_project('image 3', 'project 1')
        self.db.image.delete_with_name_from_project('image 4', 'project 1')
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestDelete(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.image.insert('image 1', 1)

    def test_run(self):
        self.db.image.delete_with_name_from_project('image 1', 'project 1')
        images = self.db.image.fetch_images_from_project('project 1')
        yes = 'image 1' in images
        self.assertFalse(yes)

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestFetch(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_public=True)
        self.db.image.insert('image 3', 1, is_provision_clone=True)
        self.db.image.insert('image 4', 1, is_snapshot=True)

    def test_run(self):
        images = self.db.image.fetch_images_from_project('project 1')
        yes = 'image 1' in images and 'image 2' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_clones_from_project('project 1')
        yes = 'image 3' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_snapshots_from_project('project 1')
        yes = 'image 4' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_names_with_public()
        yes = 'image 2' in images
        self.assertTrue(yes)

        name = self.db.image.fetch_name_with_id(1)
        self.assertEqual(name, 'image 1')

        img_id = self.db.image.fetch_id_with_name_from_project('image 2',
                                                               'project 1')
        self.assertEqual(img_id, 2)

        images = self.db.image.fetch_all_images()
        self.assertEqual(images.__len__(), 4)
        self.assertEqual([image[1] for image in images],
                         ['image 1', 'image 2', 'image 3', 'image 4'])

    def tearDown(self):
        self.db.image.delete_with_name_from_project('image 1', 'project 1')
        self.db.image.delete_with_name_from_project('image 2', 'project 1')
        self.db.image.delete_with_name_from_project('image 3', 'project 1')
        self.db.image.delete_with_name_from_project('image 4', 'project 1')
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestCopy(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.project.insert('project 2', 'network 2')
        self.db.image.insert('image 1',1)
        self.db.image.insert('image 2',1,is_snapshot=True)

    def test_run(self):
        self.db.image.copy_image('image 1','project 1','',2)
        self.db.image.copy_image('image 2','project 1','image 3',2)

        images = self.db.image.fetch_images_from_project('project 2')
        yes = 'image 1' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_snapshots_from_project('project 2')
        yes = 'image 3' in images
        self.assertTrue(yes)

    def tearDown(self):
        self.db.image.delete_with_name_from_project('image 1','project 1')
        self.db.image.delete_with_name_from_project('image 2','project 1')
        self.db.image.delete_with_name_from_project('image 1','project 2')
        self.db.image.delete_with_name_from_project('image 3','project 2')
        self.db.project.delete_with_name('project 1')
        self.db.project.delete_with_name('project 2')
        self.db.close()


class TestMove(TestCase):
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.project.insert('project 2', 'network 2')
        self.db.image.insert('image 1',1)
        self.db.image.insert('image 2',1,is_snapshot=True)

    def test_run(self):
        self.db.image.move_image('project 1','image 1',2,'')
        self.db.image.move_image('project 1','image 2',2,'image 3')

        images = self.db.image.fetch_images_from_project('project 2')
        yes = 'image 1' in images
        self.assertTrue(yes)

        images = self.db.image.fetch_snapshots_from_project('project 2')
        yes = 'image 3' in images
        self.assertTrue(yes)

    def tearDown(self):
        self.db.image.delete_with_name_from_project('image 1','project 1')
        self.db.image.delete_with_name_from_project('image 2','project 1')
        self.db.image.delete_with_name_from_project('image 1','project 2')
        self.db.image.delete_with_name_from_project('image 3','project 2')
        self.db.project.delete_with_name('project 1')
        self.db.project.delete_with_name('project 2')
        self.db.close()
