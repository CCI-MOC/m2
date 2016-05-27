import time
import unittest

from operations import *


class TestOperations(unittest.TestCase):
    def test_provision(self):
        # output = provision("http://127.0.0.1:6501/", "haasadmin", "admin123##", "super-37")
        # print output
        # self.assertEqual(output['status_code'], 500)

        good_bmi = BMI("haasadmin", "admin1234")
        bad_bmi = BMI("haasadmin", "admin123##")

        output = bad_bmi.provision("super-37")
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.provision("super-37", img_name="i12")
        print output
        self.assertEqual(output['status_code'], 404)

        time.sleep(30)

        output = good_bmi.detach_node("super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = good_bmi.provision("super-37", snap_name="hello")
        print output
        self.assertEqual(output['status_code'], 404)

        time.sleep(30)

        output = good_bmi.detach_node("super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = good_bmi.provision("super-37")
        print output
        self.assertEqual(output['status_code'], 200)

        output = good_bmi.provision("super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        time.sleep(30)

        output = good_bmi.provision("super-37")
        print output
        self.assertEqual(output['status_code'], 500)

        # output = detach_node("http://127.0.0.1:6501/", "haasadmin", "admin123##", "super-37")
        # print output
        # self.assertEqual(output['status_code'], 500)

        output = bad_bmi.detach_node("super-37")
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.detach_node("super-37")
        print output
        self.assertEqual(output['status_code'], 200)

        output = good_bmi.detach_node("super-37")
        print output
        self.assertEqual(output['status_code'], 500)

    def test_create_snapshot(self):
        good_bmi = BMI("haasadmin", "admin1234")
        bad_bmi = BMI("haasadmin", "admin123##")

        print "create snapshot"
        output = bad_bmi.create_snapshot('bmi_penultimate', 'HadoopMaster.img',
                                         'blblb1')
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.create_snapshot('bmi_penultimate',
                                          'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision")

        output = good_bmi.create_snapshot('bmi_penultimate',
                                          'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1)
        imgr.insert("HadoopMaster.img", 1,id=2)

        output = good_bmi.create_snapshot('bmi_penultimate',
                                          'hadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        output = good_bmi.create_snapshot('bmi_penultimate',
                                          'HadoopMaster.img', 'blblb1')
        print output
        self.assertEqual(output['status_code'], 200)

        pr.delete_with_name("bmi_penultimate")

        print "list snapshots"
        output = bad_bmi.list_snaps('bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.list_snaps('bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision", id=1)

        output = good_bmi.list_snaps('bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1, id=1)
        imgr.insert("HadoopMaster.img", 1, id=2)

        output = good_bmi.list_snaps('bmi_penultimate', 'hadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 404)

        output = good_bmi.list_snaps('bmi_penultimate', 'HadoopMaster.img')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 5)
        self.assertEqual(output['retval'][4], 'blblb1')

        output = good_bmi.create_snapshot('bmi_penultimate', 'HadoopMaster.img',
                                          'blblb1')
        print output
        self.assertEqual(output['status_code'], 471)

        pr.delete_with_name("bmi_penultimate")

        print "remove snapshots"
        output = bad_bmi.remove_snaps('bmi_penultimate', 'HadoopMaster.img',
                                      'blblb1')
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.remove_snaps('bmi_penultimate', 'HadoopMaster.img',
                                       'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision", id=1)

        output = good_bmi.remove_snaps('bmi_penultimate',
                                       'HadoopMaster.img',
                                       'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        imgr = ImageRepository()
        imgr.insert("hadoopMaster.img", 1, id=1)
        imgr.insert("HadoopMaster.img", 1, id=2)

        output = good_bmi.remove_snaps('bmi_penultimate',
                                       'hadoopMaster.img',
                                       'blblb1')
        print output
        self.assertEqual(output['status_code'], 404)

        output = good_bmi.remove_snaps('bmi_penultimate', 'HadoopMaster.img',
                                       'blblb1')
        print output
        self.assertEqual(output['status_code'], 200)

        pr.delete_with_name("bmi_penultimate")

    def test_list_all_images(self):
        good_bmi = BMI("haasadmin", "admin1234")
        bad_bmi = BMI("haasadmin", "admin123##")

        output = bad_bmi.list_all_images('bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 401)

        output = good_bmi.list_all_images('bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 404)

        pr = ProjectRepository()
        pr.insert("bmi_penultimate", "bmi_provision")

        output = good_bmi.list_all_images('bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 0)
        self.assertEqual(output['retval'], [])

        imgr = ImageRepository()
        imgr.insert("testimage", 1)

        output = good_bmi.list_all_images('bmi_penultimate')
        print output
        self.assertEqual(output['status_code'], 200)
        self.assertEqual(output['retval'].__len__(), 1)
        self.assertEqual(output['retval'][0], 'testimage')

        pr.delete_with_name("bmi_penultimate")
