import unittest
from mainserver import MainServer

class TestClass(unittest.TestCase):
	def test_concatenation_function(self):
		'''
		This test is done to make sure proper file name is taken from the JSON file 
		and the argument is properly concatenated
		'''
		list_of_commands = ['1', '/home']
		ms1 = MainServer()
		op = ms1.concatenate_command(list_of_commands)
		self.assertEqual(op,"./print_directory.sh /home")
	
	def test2(self):
		'''
		Check for correct number of arguments. print_directory.sh accepts only one argument.
		The function check_argument_list_length() should return false.
		'''
		concatenated_command = './print_directory.sh /home | rm -rf /home'
		ms2 = MainServer()
		self.assertFalse(ms2.correct_argument_list_length(concatenated_command,'1'))
	
	def test3(self):
		'''
		Check for the correct number of arguments. print_directory accepts one argument.
		So './print_directory.sh /home' should return true for check_argument_list().
		'''
		concatenated_command = './print_directory.sh /home'
		ms3 = MainServer()
		self.assertTrue(ms3.correct_argument_list_length(concatenated_command,'1'))

	def test_length_of_the_command_test(self):
		'''
		Length of the command given in a string form in command  line
		'''
		concatenated_command = './print_directory.sh /home | rm -rf /home'
		ms4 = MainServer()
		self.assertEqual(len(ms4.split_command(concatenated_command)),6)

	def test_check_escape_characters(self):
		'''
		Escape characters shouldn't be allowed to be passed into execution stage.
		'''
		concatenated_commands = './print_directory.sh /home/centos/rpc>test.txt'
		#Individual characters in the list needs to be tested to make sure
		#there is no escape characters in them.
		ms5 = MainServer()
		self.assertTrue(ms5.escape_characters_present(concatenated_commands))
		
	def test_check_escape_characters_2(self):
		'''
		Commands with escape characters shouldn't be allowed to run.
		'''
		list_of_commands = ['1','/home/centos/rpc;rmdir']
		ms6 = MainServer()
		self.assertEqual(ms6.run_script(list_of_commands),"The Number of arguments passed was wrong, please make sure you don't pass a command")
		
	def test_check_escape_characters_3(self):
		'''
                Commands with escape characters shouldn't be allowed to run.
                '''
                list_of_commands = ['1','/home']
                ms6 = MainServer()
                self.assertEqual(ms6.run_script(list_of_commands),"centos\n")

	def test_check_escape_characters_4(self):
		'''
		Command shouldn;t print any out just the error message.
		'''
		concatenated_command = './print_directory.sh /home/centos;echo "hi">>slurm.conf'
		ms7 = MainServer()
		self.assertTrue(ms7.escape_characters_present(concatenated_command))

	def test_print_error_message_1(self):
		'''
		This should print error message. And not display any output on the screen
		'''
		list_of_commands = ['1','/home/centos;echo','"hi">>slurm.conf']
		ms8 = MainServer()
		self.assertEqual(ms8.run_script(list_of_commands),"The Number of arguments passed was wrong, please make sure you don't pass a command")                  


if __name__ == '__main__':
	ms = MainServer()
	unittest.main()
