import unittest
from unittest import TestCase

from ims.database.database import *


class TestInsert(TestCase):
    @trace
    def setUp(self):
        self.db = Database()

    def test_run(self):
        self.db.project.insert('project 1', 'network 1')

        projects = self.db.project.fetch_projects()

        self.assertEqual('project 1', projects[0][1])

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()


class TestDelete(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def test_run(self):
        self.db.project.delete_with_name('project 1')
        projects = self.db.project.fetch_projects()
        yes = 'project 1' in projects
        self.assertFalse(yes)

    def tearDown(self):
        self.db.close()


class TestFetch(TestCase):
    @trace
    def setUp(self):
        self.db = Database()
        self.db.project.insert('project 1', 'network 1')

    def test_run(self):
        projects = self.db.project.fetch_projects()
        yes = 'project 1' in projects[0]
        self.assertTrue(yes)

        pid = self.db.project.fetch_id_with_name('project 1')
        self.assertEqual(pid, 1)

    def tearDown(self):
        self.db.project.delete_with_name('project 1')
        self.db.close()
