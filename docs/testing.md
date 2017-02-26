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
/tests/einstein/operations/unit/...
/tests/einstein/operations/integration/...
```

Every file must have a folder for itself which has additional folders called
'unit' and 'integration'

All the unit tests should be in unit folder and all integration tests should
be in integration folder for that file

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
* Each setUp method should use the trace decorator
* setUp method is supposed to do stuff which is required before the actual test
is run like adding db entries, etc.
* runTest should do the actual test and assertions to make sure everything went
 well.
* tearDown is supposed to do cleanup most commonly undo what was done in setUp
like delete db entries, etc.
 
Each test case should be independent of running order, the setUp and tearDown
methods should handle this.
 
It is fine if a failed test case causes subsequent tests to fail.
 
Each test can use the test variables in the config file
 
```
import ims.common.config as config
 
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

We made a testing framework that collects and runs tests. So follow these steps

* Write a proper bmiconfig.cfg
* Set the variable BMI_CONFIG
```
export BMI_CONFIG=<path>
```
* Some tests may require Picasso and Einstein to be running so do that if
required before proceeding.
* Run the test_ims.py file as
```
python test_ims.py run <patterns>
```
The script takes any number of regex expressions and collects test cases whose
fully qualified name matches atleast one of these regexes

For example there is a test case with fully qualified name as
database.project.unit.test_project.TestDelete

Here
* To run this Test Case just test_project.TestDelete can be given as regex
* To run all Test Cases in test_project module then test_project.\* can be
given as regex
* To run all Test Cases in database package then database.\* can be given as
regex
* To run all Unit Test Cases in database package then database.\*.unit.\* can
be given as regex
* To run all Test Cases from database and einstein pacakge then database.\* and
 einstein.\* can be given as regex
* To run all Test Cases .\* can be given as regex

There is an -i option that shows you all the test cases that matched the regex
before running them.

do python test_ims.py --help for details.
