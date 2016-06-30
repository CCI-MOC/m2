from ims.database import *

pr = ProjectRepository()
pr.insert("bmi_infra","bmi-provision")

imgr = ImageRepository()
imgr.insert("centos-6.7",1)
imgr.insert("i12",1)
