We have a basic set of API as of now. All of the services as of now are taking the arguments as parameters and return response.
BMI API assumes that you know the image which you are interested in. It has following terminology:

Project - A project is the HaaS project that has been allocated to tenant.
node - A node that is allocated to project by HaaS.
img_name - The name of image which will be used for provisioning.


Provision:

Provision API is needed for provisioning a node from MOC cluster as of now. Following is the call for API:

http://BMI_SERVER:PORT/provision?project=<project_name>&node=<node_name>&img_name=<image_name>

Ex:

https://<BMI_SERVER>:<PORT>/provision?project=bmi_infra&node=cisco-41&img_name=HadoopMaster.img

This returns either a 200 as response or other exceptions. For detailed list of exceptions, please see exceptions.

Remove:
http://BMI_SERVER:PORT/remove?

List:
http://BMI_SERVER:PORT/list_images?project=<project_name>

This returns either a list of images in response body along with 200 response or other exceptions. For detailed list of exceptions, please see exceptions.

