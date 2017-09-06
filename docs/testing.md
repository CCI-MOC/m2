# Testing BMI

Every Developer will need to test their feature or make sure that they
did not break anything. So the test cases are situated in

```
/tests/
```

## Directory Structure

This folder follows the directory structure of the project with additional
folders like for example operation.py's test cases are situated in
```
/tests/unit/einstein/...
/tests/integration/einstein/...
/tests/stress/einstein/...
```

All the unit tests should be in unit folder, all integration tests should
be in integration folder and all stress tests should be in stress folder.

Each folder should have a folder structure similar to ims and all tests should
go accordingly

All of these folders are python packages so they should have a \_\_init\_\_.py

## Writing Tests

Create a file in the correct location of the directory structure and make sure
the name conforms to the regex 'test_\*.py'

We are using python's unittest as our testing framework for now.

So the file can have any number of test cases as long as it makes sense they
belong together.

Each test case is represented by a class and should extend unittest.TestCase

This is the typical structure of a test case

```
from ims.common import config
config.load()
from ims.common.log import trace

class TestSample(unittest.TestCase):

  @trace
  def setUp(self):
       pass

  def runTest(self):
       pass

  def tearDown(self):
       pass
 ```
 
* Each class's name should start with Test
* Add a doc string for the class describing about the test.
* Each setUp method should use the trace decorator
* setUp method is supposed to do stuff which is required before the actual test
is run like adding db entries, etc.
* runTest should do the actual test and assertions to make sure everything went
 well.
* A test case class can have multiple test functions if setUp and tearDown match
for all of them (runTest shouldnt be present in this case). Also in this case
add a doc string for every test function along with the class.
* tearDown is supposed to do cleanup most commonly undo what was done in setUp
like delete db entries, etc.
 
Each test case should be independent of running order, the setUp and tearDown
methods should handle this.
 
It is fine if a failed test case causes subsequent tests to fail.
 
Each test can use the test variables in the config file
 
```
from ims.common import config
 
cfg = config.get()
 
IMAGE_NAME = cfg.tests.image_name
```
The above example is the way to access these variables
 
Any key value pair declared in the [tests] section of the config will be
available in cfg.tests variable.
 
The current values that are available in our CI are

* picasso_url
* correct_hil_username
* correct_hil_password
* incorrect_hil_password
* node_name
* nic
* project
* network
* exist_img_name
* new_snap_name
* not_exist_snap_name
* not_exist_img_name

Let us know if your test cases need additional variables

## Running Tests

We have decided to use [pytest](http://docs.pytest.org/en/latest/) as our test runner. So follow these steps

* Install pytest if its not installed
* Write a proper bmiconfig.cfg
* Set the variable BMI_CONFIG
```
export BMI_CONFIG=<path>
```
* Export the variable PYTHONPATH to the root of the ims project similar to above.
* Some tests may require Picasso and Einstein to be running so do that if
required before proceeding.
* Run pytest with the options
```
pytest tests/unit/* (Will run all unit tests)
pytest tests/integration/* (will run all integration tests)
pytest tests/stress/* (Will run all stress tests)
```
* Wait for them to run and see the results.

pytest can take the paths of test files as arguments, this can allow the dev to run 
specific test cases.
```
pytest tests/unit/database/* tests/unit/einstein/* (Will run all unit tests for db and einstein)
```

To run specific test case in a file the arguments along with -k option can be used that 
takes a python expression and runs test cases that match it.
```
pytest -k 'TestInsert' tests/unit/database/test_project.py (Run InsertTest from test_project) 
```

The tests can also be run using unittest by using the command
```
python -m unittest discover
```
Refer the python [docs](https://docs.python.org/2/library/unittest.html#test-discovery) for more options.

## Debugging Tips
Debugging strategies vary from developer to developer, we put together some tips that
might be useful.

* If a test fails, then it is better to refer bmi logs. They will be located in the folder
specified in config.
* Delete the old log before running the test again as it may reduce confusion. (You can back 
it up if you need it).
* It might be difficult to tell where a particular test started in the logs, just search for
the test's class name (like TestProvision) in the logs. The first line it hits is the start of
the test case, then the next hit is the second execution of the same test.
* --pdb option can be used along with pytest to invoke pdb when error is hit.
* When using pdb run rpc_server and name_server separately instead of using einstein_server 
command.
* If getting config errors, double check BMI_CONFIG env variable and the config file.


