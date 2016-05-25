import time
import unittest

from operations import *


class TestOperations(unittest.TestCase):
    def test_provision(self):
        # output = provision("http://127.0.0.1:6501/", "haasadmin", "admin123##", "super-37")
        # print output
        # self.assertEqual(output['status_code'], 500)

        output = provision("haasadmin", "admin123##", "super-37")
        print output
        self.assertEqual(output['status_code'], 401)

        output = provision("haasadmin", "admin1234", "super-37", img_name="i12")
        print output
        self.assertEqual(output['status_code'], 404)

        time.sleep(30)

        output = detach_node("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = provision("haasadmin", "admin1234", "super-37",
                           snap_name="hello")
        print output
        self.assertEqual(output['status_code'], 404)

        time.sleep(30)

        output = detach_node("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = provision("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 200)

        output = provision("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = provision("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        # output = detach_node("http://127.0.0.1:6501/", "haasadmin", "admin123##", "super-37")
        # print output
        # self.assertEqual(output['status_code'], 500)

        output = detach_node("haasadmin", "admin123##", "super-37")
        print output
        self.assertEqual(output['status_code'], 401)

        output = detach_node("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 200)

        output = detach_node("haasadmin", "admin1234", "super-37")
        print output
        self.assertEqual(output['status_code'], 500)

    def test_create_snapshot(self):
        print "create snapshot"
        output = create_snapshot("haasadmin", "admin123##", 'bmi_penultimate',
                                 'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 401)

        output = create_snapshot("haasadmin",
                                 "admin1234", 'bmi_penultimate',
                                 'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision")

        output = create_snapshot("haasadmin",
                                 "admin1234", 'bmi_penultimate',
                                 'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1)
        imgr.insert("HadoopMaster.img", 1)

        output = create_snapshot("haasadmin",
                                 "admin1234", 'bmi_penultimate',
                                 'hadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        output = create_snapshot("haasadmin",
                                 "admin1234", 'bmi_penultimate',
                                 'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 200)

        pr.delete_with_name("bmi_penultimate")

        print "list snapshots"
        output = list_snaps("haasadmin", "admin123##",
                            'bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 401)

        output = list_snaps("haasadmin", "admin1234",
                            'bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision", id=1)

        output = list_snaps("haasadmin", "admin1234",
                            'bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1, id=1)
        imgr.insert("HadoopMaster.img", 1, id=2)

        output = list_snaps("haasadmin", "admin1234",
                            'bmi_penultimate', 'hadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        output = list_snaps("haasadmin", "admin1234",
                            'bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 5)
        self.assertEqual(output['retval'][4], 'blblb1')

        # Not able to raise Image Exists Exception
        output = create_snapshot("haasadmin",
                                 "admin1234", 'bmi_penultimate',
                                 'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 471)

        pr.delete_with_name("bmi_penultimate")

        print "remove snapshots"
        output = remove_snaps("haasadmin",
                              "admin123##", 'bmi_penultimate',
                              'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 401)

        output = remove_snaps("haasadmin",
                              "admin1234", 'bmi_penultimate',
                              'HadoopMaster.img',
                              'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision", id=1)

        output = remove_snaps("haasadmin",
                              "admin1234", 'bmi_penultimate',
                              'HadoopMaster.img',
                              'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1, id=1)
        imgr.insert("HadoopMaster.img", 1, id=2)

        output = remove_snaps("haasadmin",
                              "admin1234", 'bmi_penultimate',
                              'hadoopMaster.img',
                              'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        output = remove_snaps("haasadmin",
                              "admin1234", 'bmi_penultimate',
                              'HadoopMaster.img',
                              'blblb1')
        print output
        self.assertEqual(output['status_code'], 200)

        pr.delete_with_name("bmi_penultimate")

    def test_list_all_images(self):
        output = list_all_images("haasadmin",
                                 "admin123##", 'bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 401)

        output = list_all_images("haasadmin",
                                 "admin1234", 'bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision")

        output = list_all_images("haasadmin",
                                 "admin1234", 'bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 0)
        self.assertEqual(output['retval'], [])

        imgr = ImageRepository()
        imgr.insert("testimage", 1)

        output = list_all_images("haasadmin",
                                 "admin1234", 'bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 1)
        self.assertEqual(output['retval'][0], 'testimage')

        pr.delete_with_name("bmi_penultimate")
