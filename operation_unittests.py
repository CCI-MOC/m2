#! /usr/bin/python

import unittest
import os
from operations import *
import uuid
class Tests(unittest.TestCase):
    def setUp(self):
        self.fsconfig = GlobalConfig()
        self.fs_obj = init_fs(self.fsconfig) 
        print self.fs_obj

    def tearDown(self):
        self.fs_obj.tear_down()
        del self.fs_obj 
        del self.fsconfig

    def test_provision(self):    
        rnd_str = str(uuid.uuid4())
        if provision( self.fs_obj, rnd_str):
            img_list = self.fs_obj.list_n()
            self.assertTrue(rnd_str in img_list)
            self.fs_obj.remove(rnd_str) 
        else:
            self.assertFalse(True) 

    def test_removal(self):    
        try:
            rnd_str = str(uuid.uuid4())
            if provision( self.fs_obj, rnd_str):
                self.fs_obj.remove(rnd_str) 
                img_list = self.fs_obj.list_n()
                self.assertFalse(rnd_str in img_list)
            else:
                self.assertFalse(False) 
        except:
            self.fs_obj.tear_down()
            del self.fsconfig
            del self.fs_obj 



if __name__ == "__main__":
    unittest.main()                 
