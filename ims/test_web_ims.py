import time
import unittest
import requests

from operations import *


class TestOperations(unittest.TestCase):
    def test_provision(self):

        url = "http://192.168.122.125:8000/BMI/default/"

        data = {"node":"super-37","img":"i12","snap_name":"HadoopGoldenImage"}
        res = requests.put(url+"provision_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        time.sleep(30)

        data = {"node":"super-37"}
        res = requests.delete(url+"remove_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        time.sleep(30)

        data = {"node":"super-37","img":"hadoopMaster.img","snap_name":"hello"}
        res = requests.put(url+"provision_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        time.sleep(30)

        data = {"node":"super-37"}
        res = requests.delete(url+"remove_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        time.sleep(30)

        data = {"node":"super-37","img":"hadoopMaster.img","snap_name":"HadoopMasterGoldenImage"}
        res = requests.put(url+"provision_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,200)

        data = {"node":"super-37","img":"hadoopMaster.img","snap_name":"HadoopMasterGoldenImage"}
        res = requests.put(url+"provision_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        time.sleep(30)

        data = {"node":"super-37","img":"hadoopMaster.img","snap_name":"HadoopMasterGoldenImage"}
        res = requests.put(url+"provision_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        data = {"node":"super-37"}
        res = requests.delete(url+"remove_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,200)

        data = {"node":"super-37"}
        res = requests.delete(url+"remove_node/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

    def test_create_snapshot(self):
        url = "http://192.168.122.125:8000/BMI/default/"

        print "create snapshot"

        data = {"project":"bmi_penultimat","img":"HadoopMaster.img","snap_name":"blblb1"}
        res = requests.put(url + "snap_image/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        data = {"project":"bmi_penultimate","img":"HadoopMaster","snap_name":"blblb1"}
        res = requests.put(url + "snap_image/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"hadoopMaster.img","snap_name":"blblb1"}
        res = requests.put(url + "snap_image/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"HadoopMaster.img","snap_name":"blblb1"}
        res = requests.put(url + "snap_image/",data=data)
        print res.content
        self.assertEqual(res.status_code,200)

        print "list snapshots"

        data = {"project":"bmi_penultimat","img":"HadoopMaster.img"}
        res = requests.post(url + "list_snapshots/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        data = {"project":"bmi_penultimate","img":"HadoopMaster"}
        res = requests.post(url + "list_snapshots/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"hadoopMaster.img"}
        res = requests.post(url + "list_snapshots/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"HadoopMaster.img"}
        res = requests.post(url + "list_snapshots/",data=data)
        print res.content
        self.assertEqual(res.status_code,200)
        # self.assertEqual(res.content)

    #     output = good_bmi.list_snaps('bmi_penultimate', 'HadoopMaster.img')
    #     print output
    #     self.assertEqual(output['status_code'], 200)
    #     self.assertEqual(output['retval'].__len__(), 5)
    #     self.assertEqual(output['retval'][4], 'blblb1')

        data = {"project":"bmi_penultimate","img":"HadoopMaster.img","snap_name":"blblb1"}
        res = requests.put(url + "snap_image/",data=data)
        print res.content
        self.assertEqual(res.status_code,471)

        print "remove snapshots"

        data = {"project":"bmi_penultimat","img":"HadoopMaster.img","snap_name":"blblb1"}
        res = requests.delete(url + "remove_snapshot/",data=data)
        print res.content
        self.assertEqual(res.status_code,500)

        data = {"project":"bmi_penultimate","img":"HadoopMaster","snap_name":"blblb1"}
        res = requests.delete(url + "remove_snapshot/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"hadoopMaster.img","snap_name":"blblb1"}
        res = requests.delete(url + "remove_snapshot/",data=data)
        print res.content
        self.assertEqual(res.status_code,404)

        data = {"project":"bmi_penultimate","img":"HadoopMaster.img","snap_name":"blblb1"}
        res = requests.delete(url + "remove_snapshot/",data=data)
        print res.content
        self.assertEqual(res.status_code,200)

    # def test_list_all_images(self):
    #     good_bmi = BMI("haasadmin", "admin1234")
    #     bad_bmi = BMI("haasadmin", "admin123##")
    #
    #     output = bad_bmi.list_all_images('bmi_penultimate')
    #     print output
    #     self.assertEqual(output['status_code'], 401)
    #
    #     output = good_bmi.list_all_images('bmi_penultimate')
    #     print output
    #     self.assertEqual(output['status_code'], 404)
    #
    #     pr = ProjectRepository()
    #     pr.insert("bmi_penultimate", "bmi_provision")
    #
    #     output = good_bmi.list_all_images('bmi_penultimate')
    #     print output
    #     self.assertEqual(output['status_code'], 200)
    #     self.assertEqual(output['retval'].__len__(), 0)
    #     self.assertEqual(output['retval'], [])
    #
    #     imgr = ImageRepository()
    #     imgr.insert("testimage", 1)
    #
    #     output = good_bmi.list_all_images('bmi_penultimate')
    #     print output
    #     self.assertEqual(output['status_code'], 200)
    #     self.assertEqual(output['retval'].__len__(), 1)
    #     self.assertEqual(output['retval'][0], 'testimage')
    #
    #     pr.delete_with_name("bmi_penultimate")
        pass