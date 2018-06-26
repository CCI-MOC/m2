# Overview

This file describes the simplified proposal (after the discussion with the larger MOC group) for the BMI REST API.

# BMI Core Resources

* Provisioned Instance - Bare-Metal/Virtual machine instance attached with a boot image.
* Image/Snapshot - A virtual disk (a.k.a. golden image) whose clone (linked clone) is used to provision an instance. Snapshot is created from an existing provisioned image by the user, while an image is uploaded by the user.
* Tag - A lighweight checkpoint of the exsiting disk image state.

# BACKGROUND

* The re-designed version of BMI can provision either Bare-Metal machines (physical servers) or Virtual machines.
* BMI now follows a driver based model.
* Below is the list of driver interfaces:
  * Diskless Provisioning: This interfaces exposes function signatures pertaining to provisioning related operations (e.g. (De)-Provisioning, Migration, etc.).
  * Storage: This interfaces exposes function signatures pertaining to image management operations (e.g. Cloning,  Snapshotting, Tagging, etc.)
  * Authentication (Optional): This interfaces exposes function signatures pertaining to legitimacy verification of the `entity` requesting a BMI operation.
  * Authorization (Optional): This interfaces exposes function signatures pertaining to `entity-resource` ownership verification.  
  * Multi-Tenancy (Optional): This interfaces exposes function signatures pertaining to maintaining isolation between different entities using the same BMI service.
* Each driver may choose to maintain table(s) in the BMI database that are visible to BMI Core and the driver itself. These table(s) are not visible between drivers.
* Entity: Project's/User's accessing BMI service are registered with an authentication service. BMI will talk to the authentication service to verify whoever calls the BMI API. 
* Quota: Each `entity` will have a default allocated storage quota (as specified by the BMI admin in the configuration file). An admin may choose to update the default quota of any Project/User.
* A BMI generated UUID is associated to each resource that helps identifying the resource. 
* A resource name has to be unique for an entity but different entities may have same resource name.
* BMI expects that the authentication service provides a unique identifier (associated with an entity) with the response - upon successful authentication.

# REST API call semantics

* An HTTP method and URL path, including possible `<parameters>` in the path to be treated as arguments.
* A summary of the request body (which will always be a JSON
  object).
* A human readable description of the semantics of the call.
* A summary of the response body for a successful request.
* Any authorization requirements, which could include:
  * Administrative access
  * No special access
 In general, administrative access is sufficient to perform any action.
* A list of possible errors.
* A user should only perform an `<action>` on a `<resource>` that he owns or is shared with him by another user.
* `Admin` is a privileged user who can perform an `<action>` on any `<resource>` that belongs to any user.

#### Possible error codes for BMI API:

* 400 - Invalid Parameters
* 401 - Invalid Credentials
* 403 - Insufficient Permissions
* 404 - Resource Does Not Exist
* 409 - Resource Busy
* 423 - Duplicate Operation
* 500 - Server/Internal Error

Below are examples how to document a BMI REST API call:

`<HTTP-method-type> /<resource>/<Id>`

**OR**

`<HTTP-method-type> /<resource>/<Id>/<action>`

The goal is to have unique `REST method URL`. Therefore, for some cases we should pass `<action>` as part of URL too.

**NOTE**: `HTTP-method-type` can be `POST`, `PUT`, `PATCH`, `GET` or `DELETE`.
* `POST` is used when a new instance of a resource is created, therefore there is no `Id` in the API call. The response body should include the `Id` for the new instance.

* `PUT` is used when an existent instance needs to be changed/updated (all attributes will be updated), it returns a status indicating if it was successful or not.

* `PATCH` is used when an existent instance needs to be changed/updated slightly (a few attributes will be updated), it returns a status indicating if it was successful or not.

* `GET` is used to read an instance or list of instances. The response will be in JSON format in case of success and otherwise an error message.

* `DELETE` is used for deleting an instance, and its response will a status indicating if it was successful or not.

#### Request Body Example (Optional - Depending on `<HTTP-method-type>`):

    {
                "idOfTheNewInstance": "a name for new instance",
                "someField": "a value",
                "thisIsAnExample": true,
                "someOptionalField (Optional): {
                        "more-fields": 12352356,
                        ...
                }
    }

**NOTE**: After the example, an explanation for each parameter must be provided.

The response header will contain the HTTP status code:
* 200 for success
* 400, 404, etc for failure

#### Response Body Example (Success - Optional):

    {
        "someInfo": "Hello, World!",
        "numbers": [1,2,3]
    }

**Response Parameters**:
* `someInfo`: Expected `response` explanation.
* `numbers` : More explanation.

#### Response Body Example (Failure):

    {
        "errorMessage": "This is the reason for the encountered error"
    }

**NOTE**: `Response Body Example (Failure)` is not required for every API call

#### Authentication (Optional):
* If Authentication is required by REST API call then the Credentials/Token should be passed using `HTTP Basic Auth`.
* Authentication is required depending on how BMI is deployed - BMI can be deployed in two modes:
  * `Standalone`: No authentication is required.
  * `Multi-tenant`: All REST calls need to be authenticated.

#### Authorization Level:
* Depending on the `<type>` (Authorization Level), a user's REST call will be executed.
* **NOTE**: User `<type>`: `User` or `Admin`

# REST API Specifications

REST API calls exposed to the external world by the BMI-core.

## Provisioned Instance
### provision

Provision a `node` using an`image`.

`POST /provisionedInstance`

**Request Body Example**:

    {
                "instanceName": "instance01",
                "parentImageId": 1231456789 ,  
                "macAddr: "00:00:00:00:00:00",
                "nic": "net01",
                "provisionEngineId": 5,
		              "type": "PHYSICAL"
                "vlan": 1000,
                "extraParamDict": {
                        "param1": "value1",
                        "param2": "value2"
                }
    }

**Parameters**:
* `instanceName`: Name of the provioned instance.
* `parentImageId`: Id of the golden image to be used for provisioning the instace  
* `macAddr`: MAC address of the instance to be provisioned
* `nic`: Network interface of the instance to be used for provisioning (as registered in BIOS)
* `provisionEngineId`: Id of the provisioning engine to be used for provisioning
* `type`: Type of the instance to be provisioned (`PHYSICAL` or `VIRTUAL`)
* `vlan` (Optional): VLAN Number. Only required in the `Multi-tenant` mode.
* `extraParamDict` (Optional): Extra Parameters that can be passed to provide additional information required by a driver

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "provisionedInstanceId": 1
    }

**Response Parameters**:
* `provisionedInstanceId`: Unique provisioning Id of the instace

***
### migrate

Detach the image from a provisioned instance and attach it to a new node.

`PATCH /provisionedInstance/<provisionedInstanceId>`

**Request Body Example**:

    {
                "macAddr": "00:00:00:00:00:00",
                "nic": "net02"
    }

**Parameters**:
* `provisionedInstanceId`: Id of the Node that is to be migrated.
* `macAddr`: MAC address of the destination node.
* `nic`: Network interface of the destination node.

**Authorization**: User/Admin

**Response (On Success)**: No Body

***
### deprovision

Free a provisioned instance.

`DELETE  /provisionedInstance/<provisionedInstanceId>`

**Request Body**: No Body

**Parameters**:
* `provisionedInstanceId`: Id of the instance to be de-provisioned.

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### snapshot   

A deep copy of the current disk state of the instance is created.

**NOTE**: Snapshot is eventually an image, but its `isSnapshot` field in the image table is set.

`POST /provisionedInstance/<provisionedInstanceId>/snapshot`

**Request Body Example**:

    {
                "name": "ubuntu-1404-marble"    
    }

**Parameters**:
* `provisionedInstanceId`: Id of the instance
* `name`: Name of the snap which will be created

**Authorization**: User/Admin

**Response Body Example (on success)**:

    {
                "imageId": 1122334455667788
    }

**Response Parameters**:
* `imageId`: Unique Id of the created image (snapshot)

***
### tag        

A shallow copy of the current disk state of the instance is created.

`POST /provisionedInstance/<provisionedInstanceId>/tag`

**Request Body Example**:

    {
                "name": "img-01"
    }

**Parameters**:
* `provisionedInstanceId`: Id of the instance
* `name`: Name of the tag

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "tagId": 1
    }

**Response Parameters**:
* `tagId`: Globally unique Id of the created tag

***
### update-tag

Update attributes of a tag.

**Supported attributes**
* name

`PATCH /tag/<tagId>`

**Request Body Example**:

    {
        "name": "tag-01"
    }

**Parameters**:
* `name`: The new name of the tag

**Authorization**: User / Admin

**Response (on success)**: No Body

***
### delete-tag

Delete an existing tag.

`DELETE  /tag/<tagId>`

**Request Body**: No Body

#### Parameters:
* `tagId`: Id of the tag

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### list-tags

List all tags for a instance.

`GET /tag/search?provisionedInstanceId=xxx

**Request Body**: No Body

**Parameters**:
* `provisionedInstanceId`: Id of the instance

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
          "tags": [
              {"id": 1, "name": "tag1"},
              ...
              ]
    }

**Response Parameters**:
* `tags`: List of all tags created by the user

***
### show-tag

Show details of a tag.

`GET /tag/<tagId>`

**Request Body**: No Body

**Parameters**:
* `tagId`: Id of the tag

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
          "name": "tag-01"
    }

**Response Parameters**:
* `name`: Name of the tag

***
### flatten-tag

Create deep copy from tag.

`POST /tag/<tagId>/flatten`

**Request Body Example**:

    {
	  "name": "flattened-tag-01"
    }

**Parameters**:
* `tagId`: Id of the tag
* `name`: name of the flattened image 

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
          "imageId": 2
    }

**Response Parameters**:
* `imageId`: Id of the image that was created after flattening the tag

***
### list

List user's provisioned instance(s).

`GET  /provisionedInstance`

**Request Body**: No Body

**Authorization**: User/Admin

* The user will have a view of all his/her provisioned nodes by calling this function.
* With administrative privilege, all provisioned nodes will be listed by calling this function.

**Response (on success)**:

    {
                "instances": [
                    { "id": 123456789, "name": "instance01"},
                    ...
                ]

    }

**Response Parameters**:
* `nodes`: List of nodes provisioned by the user

***
### show

Show the details of user's provisioned instance.

`GET  /provisionedInstance/<provisionedInstanceId>`

**Request Body**: No Body

**Parameters**:
* `provisionedInstanceId`: Id of the instance whose details are requested

**Authorization**: User/Admin

**Response (on success)**:

    {               
            "instanceName": "instance01",
            "macAddr": "00:00:00:00:00:00",
            "imageId": 241,
            "vlan": 1000,
            "nic": "net05",
            "provisionEngineId": 1
    }

**Response Parameters**:
* `instanceName`: Name of the provisioned instance
* `macAddr`: Mac Address of the instance
* `imageId`: Image Id of golden image which is used to provision
* `vlan`: The VLAN to which the instance is connected
* `nic`: The NIC that is used to provision
* `provisionEngineId`: The provision engine that is used to provision the instance

## Quota
### update

Update allocated disk of an entity. If node request body is provided, the quota is set to default.

`PATCH /quota/<entityId>`

**Request Body Example (Optional)**:

    {
        "quota": 10.0
    }

**Parameters**:
* `entityId`: Id of the entity whoes quota needs to be updated
* `quota`: The new quota of the user (In GBs)

**Authorization**: Admin

**Response (on success)**: No Body

***
### list  

List entities whoes quota was updated.

`GET /quota`

**Request Body**: No Body

**Authorization**: Admin

**Response (on success)**:

    {
                "entities": ["entity01", "entity04", ...]
    }

**Response Parameters**:
* `entities`: List of all entities whose quota was update. 

***
### show

Show details of a user.

`GET /quota/<entityId>`

**Request Body**: No Body

**Parameters**:
* `entityId`: Id of the entity

**Authorization**: Admin

**Response (on success)**:

    {
                "entityId": 2112,
                "quota": 10.0,
                "currentUsage": 5.0
    }

**Response Parameters**:
* `entityId`: Id of the entity
* `quota`: Datastore quota allocated to entity in GBs
* `currentUsage`: Current space occupied by the user



## Image/Snapshot
### upload

Upload an image (which could be local or in a given url) to a data store.

`POST /image`

**Request Body Example**:

    {
                "name": "ubuntu-1404",
                "type": "qcow",
                "isPublic": False,
                "dataStoreId": 1,
                "url": ""
    }

**Parameters**:
* `name`: Name of the image which is about to be uploaded
* `type`: Type of image that could be raw, qcow, etc.
* `isPublic`: Is the image publically visible.
* `dataStoreId`: Id of the storage in which the image will be stored
* `url` (Optional): URL address of the image

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "imageId": 123456789
    }

**Response Parameters**:
* `imageId`: Unique Id of the image

***
### download

Fetch an image from data store to save on local disk.

`GET /image/<imageId>`

**Request Headers**:
* `Accept`: Set this header to `application/octet-stream`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body (on success)**: The image

***
### copy

Make a golden copy of source image (its Id is part of url).

`POST /image/<imageId>/copy`

**Request Body Example**:

    {
                "name": "ubuntu-1404-cassandra_new",
                "dataStoreId": 1,
		"entityId": 1232121
    }

**Parameters**:
* `name`: Name for the destination image
* `dataStoreId`(Optional): Id of the storage in which the copy image will be stored. If no `dataStoreId` is provided, source and destination datastores will be the same.
* `entityId`(Optional/Admin-only): An admin can copy images between different entities.

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "imageId": "Unique Id of the destination image"
    }

**Response Parameters**:
* `imageId`: Unique Id of the destination image

***
### update

Update attributes of an image.

**Supported Attributes**
* name
* isPublic

`PATCH /image/<imageId>`

**Request Body Example**:

    {
                "name": "ubuntu-1404-cassandra",
                "isPublic": 1
    }

**Parameters**:
* `name`: New name for the image
* `isPublic`: New visibility level of the image

**Response body (on success)**: No Body

***
### delete

Delete an image.

`DELETE /image/<imageId>`

**Request Body**: No Body

**Parameters**:
* `imageId`: Id of the image to delete

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### list

List user's images (and snapshots). In case of admin, all images (and snapshots) will be listed.

`GET /image`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
              "images": [
                    {"id": 1, "name": "img-01"},
                    ...
              ]
    }

**Response Parameters**:
* `images`: List of images for the user

***
### supported image types

List support image types

`GET /image/type`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
              "supportedImageTypes": [ "raw", "qcow", ..]
    }

**Response Parameters**:
* `supportedImageTypes`: List of supported image types

***
### show

Show details of an image.

`GET  /image/<imageId>`

**Request Headers**:
* `Accept`: Set this to `application/json`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "imageName": "ubuntu-1404",
                "ownerUserId": 123,
                "type": "raw",
                "isPublic": 0,
                "isSnapshot": 0,
                "dataStoreId": 1
    }

**Response Parameters**:
* `name`: Name of the image
* `ownerUserId`: User Id of the image's owner
* `type`: Type of image that could be crow, etc
* `isPublic`: If the image is visible publicly
* `isSnapshot`: Whether the image is snapshot or not
* `dataStoreId`: Id of the storage in which the image will be stored

## DataStore
### list  

List available datastores.

`GET /datastore`

**Request Body**: No Body

**Authorization**: User/Admin

**Response (on success)**:

    {
                "datastores": ["ceph", "lustre", ...]
    }

**Response Parameters**:
* `datastores`: List of all available datastores

## Provisioning Engine
### list  

List available datastores.

`GET /provisionEngine`

**Request Body**: No Body

**Authorization**: User/Admin

**Response (on success)**:

    {
                "provionEngine": ["tgt", "iet", ...]
    }

**Response Parameters**:
* `datastores`: List of all available provisioning engines
