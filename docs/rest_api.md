# Rest API

We have a basic set of API as of now. All of the services as of now are taking the arguments as parameters and return response.

BMI API assumes that you know the image which you are interested in. BMI has an driver which can communicate with Ceph(the file storage system that we are using for storing our images). Please make sure that you understand Ceph concepts before you play with the API.

To have a clear understanding of the API, we wish to provide the following terminology:
* project - A project is the HIL project that has been allocated to tenant.
* node - A node that is allocated to project by HIL. This node should be present in HIL.
* img - The name of image which will be used for provisioning.
* snap_name - The snapshot of the image from which you want to provision a node.
* nic - The nic used for provisioning. BMI uses this name to get the macaddress from HIL.
 This is required for generating the boot configuration file.

The convention that we are following for requests is:
* PUT - for resource creation like node creation
* DELETE - for resource deletion for node deletion
* POST - for rest of operations

**The username and password for HIL needs to be passed along using HTTP Basic Auth to each possible API call.**

Each possible API call has:
* an HTTP method and URL path
* Request body(which will always be form encoded parameters)
* A list of possible responses
* An example

---
###create_disk:

This will create a disk from a source image and return an iscsi target pointing to that image.

Following is the call for API:

####Link:
http://BMI_SERVER:PORT/create_disk/

####Request Type:
PUT

####Request Body:
```json
{
 "project" : "<project_name>",
 "disk_name" : "<disk_name>" ,
 "img_name" : "<source image>" ,
}
```

####Responses:
* 200. This means the create_disk call is successful.
* 401. Authentication Failure
* 403. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
* 409. Image busy exception.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

####Example:
Send a PUT Request with following body to http://<BMI_SERVER>:<PORT>/create_disk/

```json
{
 "project" : "bmi_infra",
 "disk_name" : "centos7-controller" ,
 "img_name" : "centos7-golden" ,
}
```
**Make sure to use HTTP Basic Auth to pass HIL Credentials**

This should return a 200 or other errors as explained above.

---
###Provision:

This call creates the boot configuration file (based on mac address) and the ipxe file that refers to the target
specified.

Following is the call for API:

####Link:
http://BMI_SERVER:PORT/provision/

####Request Type:
PUT

####Request Body:
```json
{
 "project" : "<project_name>",
 "node" : "<node_name>" ,
 "disk_name" : "<disk_name>" ,
 "nic" : "<nic to generate the boot configuration file for>"
}
```

####Responses:
* 200. This means the provision call is successful.
* 401. Authentication Failure
* 403. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
* 404. If the nic is not found or the disk is not found.
* 409. Image busy exception.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

####Example:
Send a PUT Request with following body to http://<BMI_SERVER>:<PORT>/provision/

```json
{
 "project" : "bmi_infra",
 "node" : "cisco-2016" ,
 "disk_name" : "hadoopMaster" ,
 "nic" : "nic01"
}
```
**Make sure to use HTTP Basic Auth to pass HIL Credentials**

This should return a 200 or other errors as explained above.

---
###Delete_disk:

This call will *delete* your disk.

####Link:
http://BMI_SERVER:PORT/delete_disk/

####Request Type:
DELETE

####Request Body:
```json
{
 "project" : "<project_name>",
 "disk_name" : "disk_name" ,
}
```

####Responses:
* 200. This means the delete_disk call is successful.
* 401. Authentication Failure
* 404. Disk not found
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

####Example:
Send a DELETE Request with following body to http://<BMI_SERVER>:<PORT>/deprovision/
```json
{
 "project" : "bmi_infra",
 "disk_name" : "centos7-controller" ,
}
```

---
###Deprovision:

This call deletes the boot configuration file and the ipxe file for that.
You must have the node in your hil project when making this call.

####Link:
http://BMI_SERVER:PORT/deprovision/

####Request Type:
DELETE

####Request Body:
```json
{
 "project" : "<project_name>",
 "node" : "<node_name>" ,
 "nic" : "<nic whose boot configuration file will be deleted>"
}
```

####Responses:
* 200. This means the deprovision call is successful.
* 401. Authentication Failure
* 404. Nic not found.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

####Example:
Send a DELETE Request with following body to http://<BMI_SERVER>:<PORT>/deprovision/
```json
{
 "project" : "bmi_infra",
 "node" : "cisco-2016" ,
 "nic" : "nic01"
}
```

**Make sure to use HTTP Basic Auth to pass HIL Credentials**

This should return a 200 or other errors as explained above.

---
###List Images:

Following is the call for API:

####Link:
http://BMI_SERVER:PORT/list_images/

####Request Type:
POST

####Request Body:
```json
{
 "project" : "<project_name>"
}
```

####Respones:
* 200. This means list node call is successful and it returns list of images available in your project.
* 401. Authentication Failure
* 403. This means unauthorized access to project.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

This returns either a list of images in response body along with 200 response or other exceptions.

####Example:
Send a POST Request with following body to http://BMI_SERVER:PORT/list_images/
```json
{
 "project" : "bmi_infra"
}
```

**Make sure to use HTTP Basic Auth to pass HIL Credentials**

The list of images which are in your project - if it is successful with a status code of 200.

---
###Create Snapshot:
Snapshot creates a new image that preserves the state of your disk. This allows you to
do the customization on one image and then provision other names from the snapshot.

**If the node is provisioned from the disk to be snapshotted, please power it off.**

Following is the call for API:

####Link:
http://BMI_SERVER:PORT/create_snapshot/

####Request Type:
PUT

####Request Body:
```json
{
 "project" : "<project_name>",
 "disk_name" : "<disk_name>" ,
 "snap_name" : "<snapshot_name>"
}
```

####Response:
* 200. This means the create snapshot call is successful.
* 401. Authentication Error
* 403. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
* 404. Image not found exception.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error.

####Example:
Send a PUT Request with following body to http://BMI_SERVER:PORT/create_snapshot/
```json
{
"project":"bmi_infra",
"disk_name": "centos7-base",
"snap_name":"centos7-compute"
}
```

**Make sure to use HTTP Basic Auth to pass HIL Credentials**

This should return a 200 or other errors as explained above.

---
###List Snapshots:
This returns all the snapshots associated with a project

Following is the call for API:

####Link:
http://BMI_SERVER:PORT/list_snapshots/

####Request Type:
POST

####Request Body:
```json
{
 "project" : "<project_name>"
}
```

####Response:
* 200. This means the list snapshot call is successful.
* 401. Authentication Error
* 403. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
* 404. Image not found exception.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error

####Example:
Send a POST Request with following body to http://BMI_SERVER:PORT/list_snapshots/
```json
{
 "project" : "bmi_infra"
}
```

**Make sure to use HTTP Basic Auth to pass HIL Credentials**

The list of snapshots for given image which is in your project - if it is successful with a status code of 200.

---
###Remove Image:
Following is the call for API:

####Link:
http://BMI_SERVER:PORT/remove_image/

####Request Type:
DELETE

####Request Body:
```json
{
 "project" : "<project_name>" ,
 "img" : "<img_name>"
}
```

####Response:
* 200. This means the remove snapshot call is successful.
* 401. Authentication Error.
* 403. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
* 404. Image not found exception.
* 405. You used a wrong request method like PUT instead of POST etc.
* 400. If Request is a bad one.
* 500. Internal BMI Error.

####Example:
Send a DELETE Request with following body to http://BMI_SERVER:PORT/remove_image/
```json
{
 "project" : "bmi_infra",
 "img" : "test.img"
}
```

**Make sure to use HTTP Basic Auth to pass HIL Credentials**

If the call is successful, we will get a 200 as status code and test.img should be removed.

---
