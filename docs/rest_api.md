We have a basic set of API as of now. All of the services as of now are taking the arguments as parameters and return response.

BMI API assumes that you know the image which you are interested in. BMI has an driver which can communicate with Ceph(the file storage system that we are using for storing our images). Please make sure that you understand Ceph concepts before you play with the API. 

To have a clear understanding of the API, we wish to provide the following terminology:

project - A project is the HaaS project that has been allocated to tenant.
node - A node that is allocated to project by HaaS. This node should be present in HaaS.
img - The name of image which will be used for provisioning.
snap_name - The snapshot of the image from which you want to provision a node.

The convention that we are following for requests is:

PUT - for resource creation like node creation 
DELETE - for resource deletion for node deletion
POST - for rest of operations

Each possible API call has:

-an HTTP method and URL path
-Request body(which will always be a JSON object)
-A list of possible responses
-An example

Provision:

Provision API is needed for provisioning a node from MOC cluster as of now. Provision operation internally calls a ceph clone operation. Ceph clone operation usually takes a snap_

Following is the call for API:

http://BMI_SERVER:PORT/provision_node 
with PUT request type and request body as:

{
"node" : "<node_name>" , 
"img" : "<image_name>" , 
"project" : "<project_name>" , 
"snap_name" : "<snapshot_name>"
} 

Responses:

- 200. This means the provision call is successful.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
- 403. This means a ceph connection problem.
- 409. Image busy exception.
- 444. You used a wrong request method like PUT instead of POST etc.
 
Example:

https://<BMI_SERVER>:<PORT>/provision_node
with PUT request type and request body as:

body:

{
 "node" : "cisco-2016" ,
 "img" : "hadoopMaster.img" ,
 "project" : "bmi_infra" ,
 "snap_name" : "HadoopMasterGoldenImage"
}

This should return a 200 or other errors as explained above.


Remove:

http://BMI_SERVER:PORT/delete_node
with DELETE request type and request body as:

body:

{
 "node" : "<node_name>" ,
 "project" : "<project_name>" 
}

Responses:

- 200. This means the delete node call is successful.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
- 403. This means a ceph connection problem.
- 409. Image busy exception.
- 405. Image has snapshots. (We need to delete them before we delete image).
- 404. Image not found exception.
- 444. You used a wrong request method like PUT instead of POST etc.

Example:

http://BMI_SERVER:PORT/delete_node
with DELETE request type and request body as:
body:

{
 "node" : "cisco-2016" ,
 "project" : "bmi_infra" 
}

This should return a 200 or other errors as explained above.


List:


http://BMI_SERVER:PORT/list_images
with POST request type and request body:

body:

{
 "project" : "<project_name>" 
}

- 200. This means list node call is successful 
   and it returns list of images available in your project.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to project.
- 403. This means a ceph connection problem.
- 444. You used a wrong request method like PUT instead of POST etc.

This returns either a list of images in response body along with 200 response or other exceptions. 

Example:

http://BMI_SERVER:PORT/list_images
with POST request type and request body:

body:

{
 "project" : "bmi_infra"
}

Response:

[ "img1" , "img2"....
		...., "img n"] in body

The list of images which are in your project - if it is successful with a status code of 200.

create snapshot:

Snapshot is feature which is available to preserve the state of your image. Using ceph as backend we can preserve the state of your image as a snapshot and use this snapshot for further cloning.

http://BMI_SERVER:PORT/snap_image
with PUT request type and request body as:

body:

{
 "img" : "<img_name>" ,
 "project" : "<project_name>",
 "snap_name" : "snapshot_name>" 
}

Response:
- 200. This means the create snapshot call is successful.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
- 403. This means a ceph connection problem.
- 409. Image busy exception.
- 404. Image not found exception.
- 444. You used a wrong request method like PUT instead of POST etc.

Example:

http://BMI_SERVER:PORT/snap_image
with PUT request type and request body as:

{
"project":"bmi_infra", 
"img": "test.img", 
"snap_name":"test_snap2016" 
}

This should return a 200 or other errors as explained above.

List snapshots:

We can have as many snapshots as possible for a particular image. So, using this we can list all the snapshots available for an image.

http://BMI_SERVER:PORT/list_snapshots
with POST request type and request body as:

body:

{
 "img" : "<img_name>" ,
 "project" : "<project_name>"
}

Response:
- 200. This means the list snapshot call is successful.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
- 403. This means a ceph connection problem.
- 409. Image busy exception.
- 404. Image not found exception.
- 444. You used a wrong request method like PUT instead of POST etc.

Example:

body:

{
 "img" : "test.img" ,
 "project" : "bmi_infra"
}


Response:

[ "snapshot1" , "snapshot2"....
		...., "snapshotn"] for image "test.img" in body

The list of snapshots for given image which is in your project - if it is successful with a status code of 200.

Remove snapshot:

http://BMI_SERVER:PORT/remove_snapshot
with DELETE request type and request body as:

body:

{
 "img" : "<img_name>" ,
 "project" : "<project_name>" ,
 "snap_name" : "snapshot_name>"
}

Response:
- 200. This means the remove snapshot call is successful.
- Internal 500 with some junk characters. This means the request body is not proper.
- 401. This means unauthorized access to ceph image or snapshot or image already exists in ceph.
- 403. This means a ceph connection problem.
- 409. Image busy exception.
- 404. Image not found exception.
- 444. You used a wrong request method like PUT instead of POST etc.

Example:

body:

{
 "img" : "test.img" ,
 "project" : "bmi_infra",
 "snap_name" : "test_snap2015"
}

If the call is successful, we will get a 200 as status code with test_snap2015 snapshot for image test.img will be removed.

