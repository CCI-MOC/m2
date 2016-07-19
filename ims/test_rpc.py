import unittest
from rpcclient import RPCClient
import cStringIO
import sys

class TestClass(unittest.TestCase):
    def test_invalid_argument_list_length_1(self):
        '''
        This method checks the behavior of the program when extra arguments are passed.
        '''
        rc =  RPCClient()
        list_of_commands = ['provision' , 'cisco-53' , 'hadoopMaster.img' ,\
             'HadoopMasterGoldenImage','False','extra_argument']
        stdout_ = sys.stdout #Keep track of the previous value
        stream = cStringIO.StringIO()
        sys.stdout = stream
        rc.client_function(list_of_commands)
        #To capture the print stdout
        sys.stdout = stdout_ # restore the previous stdout.
        op = stream.getvalue()
        self.assertEqual(op,'Invalid argument.\n')    


    def test_wrong_method_name_1(self):
        '''
        This method checks the behavior of the program when the method name is passed.
        '''
        rc =  RPCClient()
        list_of_commands = ['pro' , 'cisco-53'] #pro is not a defined method
        stdout_ = sys.stdout #Keep track of the previous value
        stream = cStringIO.StringIO()
        sys.stdout = stream
        rc.client_function(list_of_commands)
        #To capture the print stdout
        sys.stdout = stdout_ # restore the previous stdout.
        op = stream.getvalue()
        self.assertEqual(op,'Invalid argument.\n')
       

    def test_escape_characters_present_1(self):
        '''
        This method checks the behavior of the program when escape character is present.
        '''
        rc =  RPCClient()
        list_of_commands = ['provision' , 'cisco-53;ls'] #pro is not a defined method
        stdout_ = sys.stdout #Keep track of the previous value
        stream = cStringIO.StringIO()
        sys.stdout = stream
        rc.client_function(list_of_commands)
        #To capture the print stdout
        sys.stdout = stdout_ # restore the previous stdout.
        op = stream.getvalue()
        self.assertEqual(op,'Invalid argument.\n')
     

    def test_escape_characters_present_2(self):
        '''
        This method validates the behavior of the concatenate_command.
        '''
        rc =  RPCClient()
        list_of_commands = ['detach_node' , 'cisco-53;'] #pro is not a defined method
        stdout_ = sys.stdout #Keep track of the previous value
        stream = cStringIO.StringIO()
        sys.stdout = stream
        rc.client_function(list_of_commands)
        #To capture the print stdout 
        sys.stdout = stdout_ # restore the previous stdout.
        op = stream.getvalue()
        self.assertEqual(op,'Invalid argument.\n')
        
if __name__ == '__main__':
    rpcl = RPCClient()
    unittest.main()


