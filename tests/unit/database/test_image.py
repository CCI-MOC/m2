from unittest import TestCase

from ims.common import config
config.load()

from ims.common.log import trace
from ims.database.database import Database
from ims.exception import db_exceptions


class TestInsert(TestCase):
    """ Creates a project and tests inserting images """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def runTest(self):
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_public=True)
        self.db.image.insert('image 3', 1, parent_id=1)
        self.db.image.insert('image 4', 1, is_snapshot=True, parent_id=1)

        images = self.db.image.fetch_images_from_project('project 1')
        self.assertTrue('image 1' in images and 'image 2' in images)

        images = self.db.image.fetch_clones_from_project('project 1')
        self.assertTrue('image 3' in [img[0] for img in images])

        snapshots = self.db.image.fetch_snapshots_from_project('project 1')
        self.assertTrue('image 4' in [snapshot[0] for snapshot in snapshots])

        images = self.db.image.fetch_names_with_public()
        self.assertTrue('image 2' in images)

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestDelete(TestCase):
    """ Inserts image and deletes it """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.image.insert('image 1', 1)

    def runTest(self):
        self.db.image.delete_with_name_from_project('image 1', 'project 1')
        images = self.db.image.fetch_images_from_project('project 1')
        self.assertFalse('image 1' in images)

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestFetch(TestCase):
    """ Inserts several images and tests all fetch calls """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_public=True)
        self.db.image.insert('image 3', 1, parent_id=1)
        self.db.image.insert('image 4', 1, is_snapshot=True, parent_id=1)

    def test_image_fetch(self):
        images = self.db.image.fetch_images_from_project('project 1')
        self.assertTrue('image 1' in images and 'image 2' in images)

        images = self.db.image.fetch_clones_from_project('project 1')
        self.assertTrue('image 3' in [img[0] for img in images])

        snapshots = self.db.image.fetch_snapshots_from_project('project 1')
        self.assertTrue('image 4' in [snapshot[0] for snapshot in snapshots])

        images = self.db.image.fetch_names_with_public()
        self.assertTrue('image 2' in images)

        name = self.db.image.fetch_name_with_id(1)
        self.assertEqual(name, 'image 1')

        img_id = self.db.image.fetch_id_with_name_from_project('image 2',
                                                               'project 1')
        self.assertEqual(img_id, 2)

        images = self.db.image.fetch_all_images()
        self.assertEqual(images.__len__(), 4)
        self.assertEqual([image[1] for image in images],
                         ['image 1', 'image 2', 'image 3', 'image 4'])

    def test_nonexistent_image_fetch(self):
        """
        Tries to retrieve the image id of an image that doesn't
        exist in the db. Should raise an error
        """

        with self.assertRaises(db_exceptions.ImageNotFoundException):
            img_id = self.db.image.fetch_id_with_name_from_project(
                'nonexistent_image', 'project 1')

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestCopy(TestCase):
    """ Inserts images and tries copying them """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.project.insert('project 2', 'network 2')
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_snapshot=True, parent_id=1)

    def runTest(self):
        self.db.image.copy_image('project 1', 'image 1', 2, None)
        self.db.image.copy_image('project 1', 'image 2', 2, 'image 3')
        self.db.image.copy_image('project 1', 'image 2', 1, 'image 3')

        images = self.db.image.fetch_images_from_project('project 2')
        self.assertTrue('image 1' in images)

        snaps = self.db.image.fetch_snapshots_from_project('project 2')
        images = self.db.image.fetch_images_from_project('project 2')

        self.assertTrue('image 3' in images and
                        not ('image 3' in [s[0] for s in snaps]))

        snaps = self.db.image.fetch_snapshots_from_project('project 1')
        self.assertTrue('image 3' in [s[0] for s in snaps])

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.project.delete_with_name('project 2')
        self.db.close()


class TestMove(TestCase):
    """ Inserts images and tries moving them """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')
        self.db.project.insert('project 2', 'network 2')
        self.db.image.insert('image 1', 1)
        self.db.image.insert('image 2', 1, is_snapshot=True, parent_id=1)

    def runTest(self):
        self.db.image.move_image('project 1', 'image 1', 2, None)
        self.db.image.move_image('project 1', 'image 2', 1, 'image 3')

        images = self.db.image.fetch_images_from_project('project 2')
        images1 = self.db.image.fetch_images_from_project('project 1')
        self.assertTrue('image 1' in images and 'image 1' not in images1)

        snaps = self.db.image.fetch_snapshots_from_project('project 1')
        self.assertTrue(('image 3' in [s[0] for s in snaps]) and
                        not ('image 2' in [s[0] for s in snaps]))

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.project.delete_with_name('project 2')
        self.db.close()
