from ims.database import *

pr = ProjectRepository()
pr.insert("bmi_infra","bmi-provision")

imgr = ImageRepository()
imgr.insert("i12",1)
imgr.insert("hadoopMaster.img",1)