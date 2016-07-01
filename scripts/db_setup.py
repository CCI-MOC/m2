from ims.database import *

db = Database()
db.project.insert("bmi_infra","bmi-provision")
db.image.insert("centos-6.7",1)
db.image.insert("i12",1)
