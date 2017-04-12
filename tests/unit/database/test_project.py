from unittest import TestCase

from ims.common import config
config.load()

from ims.common.log import trace
from ims.database.database import Database


class TestInsert(TestCase):
    """ Inserts Project """

    @trace
    def setUp(self):
        self.db = Database()

    def runTest(self):
        self.db.project.insert('project 1', 'network 1')

        projects = self.db.project.fetch_projects()

        self.assertEqual('project 1', projects[0][1])

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestDelete(TestCase):
    """ Inserts and Deletes Project """

    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def runTest(self):
        self.db.project.delete_with_name('project 1')
        projects = self.db.project.fetch_projects()
        self.assertFalse('project 1' in projects)

    def tearDown(self):
        self.db.close()


class TestFetch(TestCase):
    """ Inserts and Fetches Projects """
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def runTest(self):
        projects = self.db.project.fetch_projects()
        self.assertTrue('project 1' in projects[0])

        pid = self.db.project.fetch_id_with_name('project 1')
        self.assertEqual(pid, 1)

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()
