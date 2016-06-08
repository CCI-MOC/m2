import time
import unittest
from operations import *


class TestOperations(unittest.TestCase):
    def test_provision(self):
        url = "http://192.168.122.125:8000/BMI/rest/"

        data = {"node": "super-37", "img": "i12",
                "snap_name": "HadoopGoldenImage"}
        res = requests.put(url + "provision_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        time.sleep(30)

        data = {"node": "super-37"}
        res = requests.delete(url + "remove_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        time.sleep(30)

        data = {"node": "super-37", "img": "hadoopMaster.img",
                "snap_name": "hello"}
        res = requests.put(url + "provision_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        time.sleep(30)

        data = {"node": "super-37"}
        res = requests.delete(url + "remove_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        time.sleep(30)

        data = {"node": "super-37", "img": "hadoopMaster.img",
                "snap_name": "HadoopMasterGoldenImage"}
        res = requests.put(url + "provision_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 200)

        data = {"node": "super-37", "img": "hadoopMaster.img",
                "snap_name": "HadoopMasterGoldenImage"}
        res = requests.put(url + "provision_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        time.sleep(30)

        data = {"node": "super-37", "img": "hadoopMaster.img",
                "snap_name": "HadoopMasterGoldenImage"}
        res = requests.put(url + "provision_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        data = {"node": "super-37"}
        res = requests.delete(url + "remove_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 200)

        data = {"node": "super-37"}
        res = requests.delete(url + "remove_node/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

    def test_create_snapshot(self):
        url = "http://192.168.122.125:8000/BMI/default/"

        print "create snapshot"

        data = {"project": "bmi_penultimat", "img": "HadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.put(url + "snap_image/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster",
                "snap_name": "blblb1"}
        res = requests.put(url + "snap_image/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "hadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.put(url + "snap_image/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.put(url + "snap_image/", data=data)
        print res.content
        self.assertEqual(res.status_code, 200)

        print "list snapshots"

        data = {"project": "bmi_penultimat", "img": "HadoopMaster.img"}
        res = requests.post(url + "list_snapshots/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster"}
        res = requests.post(url + "list_snapshots/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "hadoopMaster.img"}
        res = requests.post(url + "list_snapshots/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster.img"}
        res = requests.post(url + "list_snapshots/", data=data)
        print res.content
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js.__len__(),5)
        self.assertEqual(js[4],'blblb1')

        data = {"project": "bmi_penultimate", "img": "HadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.put(url + "snap_image/", data=data)
        print res.content
        self.assertEqual(res.status_code, 471)

        print "remove snapshots"

        data = {"project": "bmi_penultimat", "img": "HadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.delete(url + "remove_snapshot/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster",
                "snap_name": "blblb1"}
        res = requests.delete(url + "remove_snapshot/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "hadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.delete(url + "remove_snapshot/", data=data)
        print res.content
        self.assertEqual(res.status_code, 404)

        data = {"project": "bmi_penultimate", "img": "HadoopMaster.img",
                "snap_name": "blblb1"}
        res = requests.delete(url + "remove_snapshot/", data=data)
        print res.content
        self.assertEqual(res.status_code, 200)

    def test_list_all_images(self):
        url = "http://192.168.122.125:8000/BMI/default/"

        data = {"project": "bmi_penultimat"}
        res = requests.post(url + "list_images/", data=data)
        print res.content
        self.assertEqual(res.status_code, 500)

        data = {"project": "bmi_penultimate"}
        res = requests.post(url + "list_images/", data=data)
        print res.content
        js = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(js.__len__(),2)
        self.assertEqual(js[0],"hadoopMaster.img")
        self.assertEqual(js[1],"HadoopMaster.img")
