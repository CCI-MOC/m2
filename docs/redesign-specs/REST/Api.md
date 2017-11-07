# Overview

This file describes an initial proposal for the BMI REST API.

# Resources in BMI

* Node - Bare metal server (physical server).
* User - An entity using BMI.
* Access Control List (ACL) - List of users who may access an image.
* Image/Snapshot - A virtual disk (a.k.a. golden image) whose clone (linked clone) is used to provision a node. Snapshot is created from an existing provisioned image by the user, while an image is uploaded by the user.
* Data Store - A filesystem/service where images are stored.
* Authentication - A service used to authenticate the legitimacy of a user request.
* Provisioning Engine - A service used to (de)-provision a node.
* VLAN - Provisioning network.

# REST API call semantics

* An HTTP method and URL path, including possible `<parameters>` in the
  path to be treated as arguments.
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

## Node
### provision

Provision a `node` using an`image`.

`POST /nodes`

**Request Body Example**:

    {
                "parentImageId": 1231456789 ,  
                "macAddr: "00:00:00:00:00:00",
                "nic": "net01",
                "provisionEngineId": 5,  
                "vlan": 1000,
                "extraParamDict": {
                        "param1": "value1",
                        "param2": "value2"
                }
    }

**Parameters**:
* `parentImageId`: Id of the golden image to be used for provisioning the node  
* `macAddr`: MAC address of the node to be provisioned
* `nic`: Network interface of the node to be used for provisioning
* `provisionEngineId`: Id of the provisioning engine to be used for provisioning
* `vlan` (Optional): VLAN Number. Only required in the `Multi-tenant` mode.
* `extraParamDict` (Optional): Extra Parameters that can be passed to provide additional information required by a driver

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "nodeId": 1
    }

**Response Parameters**:
* `nodeId`: Unique provisioning Id of the node

***
### migrate

Detach the image from a provisioned node and attach it to a new node.

`PATCH /nodes/<nodeId>`

**Request Body Example**:

    {
                "macAddr": "00:00:00:00:00:00",
                "nic": "net02"
    }

**Parameters**:
* `nodeId`: Id of the Node that is to be migrated.
* `macAddr`: MAC address of the destination node.
* `nic`: Network interface of the destination node.

**Authorization**: User/Admin

**Response (On Success)**: No Body

***
### deprovision

Free a provisioned node.

`DELETE  /nodes/<nodeId>`

**Request Body**: No Body

**Parameters**:
* `nodeId`: Id of the node to be de-provisioned.

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### snapshot   

A deep copy of the current state of the node is created.

**NOTE**: Snapshot is eventually an image, but its `isSnapshot` is set.

`POST /nodes/<nodeId>/snapshot`

**Request Body Example**:

    {
                "name": "ubuntu-1404-marble"    
    }

**Parameters**:
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

A shallow copy of the current state of the node is created.

`POST /nodes/<nodeId>/tags`

**Request Body Example**:

    {
                "name": "img-01"
    }

**Parameters**:
* `nodeId`: Id of the node
* `name`: Name of the tag

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "tagId": 1
    }

**Response Parameters**:
* `tagId`: Unique Id of the created tag

***
### update-tag

Update attributes of a tag.

**Supported attributes**
* name

`PATCH /nodes/<nodeId>/tags/<tagId>`

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

`DELETE  /nodes/<nodeId>/tags/<tagId>`

**Request Body**: No Body

#### Parameters:
* `nodeId`: Id of the node
* `tagId`: Id of the tag

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### list-tags

List all tags for a node.

`GET /nodes/<nodeId>/tags`

**Request Body**: No Body

**Parameters**:
* `nodeId`: Id of the node

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

`GET /nodes/<nodeId>/tags/<tagId>`

**Request Body**: No Body

**Parameters**:
* `nodeId`: Id of the node
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

`POST /nodes/<nodeId>/tags/<tagId>/flatten`

**Request Body**: No Body

**Parameters**:
* `nodeId`: Id of the node
* `tagId`: Id of the tag

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
          "imageId": 2
    }

**Response Parameters**:
* `imageId`: Id of the image that was created after flattening the tag

***
### list

List user's provisioned nodes.

`GET  /nodes`

**Request Body**: No Body

**Authorization**: User/Admin

* The user will have a view of all his/her provisioned nodes by calling this function.
* With administrative privilege, all provisioned nodes will be listed by calling this function.

**Response (on success)**:

    {
                "nodes": [
                    { "id": 123456789, "name": "node01"},
                    ...
                ]

    }

**Response Parameters**:
* `nodes`: List of nodes provisioned by the user

***
### show

Show the details of user's provisioned node.

`GET  /nodes/<nodeId>`

**Request Body**: No Body

**Parameters**:
* `nodeId`: Id of the node whose details are requested

**Authorization**: User/Admin

**Response (on success)**:

    {                
            "macAddr": "00:00:00:00:00:00",
            "imageId": 241,
            "vlan": 1000,
            "nic": "net05",
            "provisionEngineId": 1
    }

**Response Parameters**:
* `macAddr`: Mac Address of the Node
* `imageId`: Image Id of golden image which is used to provision
* `vlan`: The VLAN to which the node is connected
* `nic`: The NIC that is used to provision
* `provisionEngineId`: The provision engine that is used to provision the node

## User
### add

Register a new user.

`POST  /users`

**Request Body Example**:

    {
                "name": "user01",
                "authenticationId": 123
    }

**Parameters**:
* `name`: Name of the new user to be created
* `authenticationId`: Id of the authentication server to be used for this user

**Authorization**: Admin

**Response (on success)**:

    {
                "userId": 1
    }

**Response Parameters**:
* `userId`: Unique Id of the user

***
### update

Update attributes of a user.

**Supported attributes**
* status
* quota

`PATCH /users/<userId>`

**Request Body Example**:

    {
        "status": "disabled",
        "quota": 10.0
    }

**Parameters**:
* `status`: The new status of the user
* `quota`: The new quota of the user (In GBs)

**Authorization**: Admin

**Response (on success)**: No Body

***
### delete

Remove an existing user.

`DELETE  /users/<userId>`

**Request Body**: No Body

**Parameters**:
* `userId`: Id of the user to be removed from the system

**Authorization**: Admin

**Response (on success)**: No Body

***
### list  

List all users.

`GET /users`

**Request Body**: No Body

**Authorization**: Admin

**Response (on success)**:

    {
                "users": [
                    { "id":1, "name":"user01"},
                    ...
                ]
    }

**Response Parameters**:
* `users`: List of all  registered users

***
### show

Show details of a user.

`GET /users/<userId>`

**Request Body**: No Body

**Parameters**:
* `userId`: Id of the user

**Authorization**: Admin

**Response (on success)**:

    {
                "name": "user01",
                "type": "user",
                "quota": 10.0,
                "status": "active",
                "authenticationId": 1
    }

**Response Parameters**:
* `name`: Name of the user
* `type`: Type of user
* `quota`: Datastore quota allocated to user in GBs
* `status`: Current status of the user
* `authenticationId`: Id of the Authentication Server

## Access Control List (ACL)
### create

Create an access control list.

`POST /acls`

**Request Body Example**:

    {
                "name": "acl-01"
    }

**Parameters**:
* `name`: Name of the access control list

**Authorization**: User/Admin

**Response body (on success)**:

    {
                "aclId": 1
    }

**Response Parameters**:
* `aclId`: Unique Id of the created access control list

***
### update

Update attributes of an access control list.

**Supported Attributes**
* name

`PATCH /acls/<aclId>`

**Request Body Example**:

    {
                "name": "acl-01"
    }

**Parameters**:
* `name`: New name of the access control list

**Authorization**: User/Admin

**Response body (on success)**: No Body

***
### add-user

Add user to an access control list.

`PUT /acl/<aclId>/users/<userId>`

**Request Body Example**: No Body

**Parameters**:
* `aclId`: Id of the access control list
* `userId`: Id of the user to add

**Authorization**: User/Admin

**Response body (on success)**: No Body

***
### remove-user

Remove user from an access control list.

`DELETE /acl/<aclId>/users/<userId>`

**Request Body Example**: No Body

**Parameters**:
* `aclId`: Id of the access control list
* `userId`: Id of the user to delete

**Authorization**: User / Admin

**Response body (on success)**: No Body

***
### update-users   

Update the list of users in an access control list.

`PUT /acls/<aclId>/users`

**Request Body Example**:

    {
                "users": [
                                "user1",
                                "user2",
                                ...
                        ]
    }

**Parameters**:
* `aclId`: Id of the access control list
* `users`: List of users to replace the users with

**Authorization**: User / Admin

**Response body (on success)**: No Body

***
### delete

Delete an access control list.

`DELETE  /acls/<aclId>`

**Request Body Example**: No Body

**Parameters**:
* `aclId`: Id of the access control list

**Authorization**: User / Admin

**Response body (on success)**: No Body

***
### list

List all access control lists to which the user belongs.

`GET /acls`

**Request Body Example**: No Body

**Authorization**: User / Admin
* In case of admin, all access control lists will be listed.

**Response body (on success)**:

    {
                "acls": [
                        {"aclId": 1, "name": "acl-01"},
                        ...
                ]
    }

**Response Parameters**:
* `acls`: The list of ACLs to which the user belongs

***
### show

Show details of an access control list.

`GET /acls/<aclId>`

**Request Body Example**: No Body

**Parameters**:
* `aclId`: Id of the access control list

**Authorization**: User / Admin

**Response body (on success)**:

    {
            "name": "acl-01",
            "users": ["user1", "user2", ...]
    }

**Response Parameters**:
* `aclId`: Id of the access control list
* `name`: Name of the access control list
* `users`: List of users in the access control list

## Image/Snapshot
### upload

Upload an image (which could be local or in a given url) to a data store.

`POST /images`

**Request Body Example**:

    {
                "name": "ubuntu-1404",
                "type": "qcow",
                "visibility": 0,
                "dataStoreId": 1,
                 "acls": [
                        1,
                        2,
                        ...
                ]
                "url": ""
    }

**Parameters**:
* `name`: Name of the image which is about to be uploaded
* `type`: Type of image that could be crow, etc
* `visibility`: Visibility of the image that could be public, semi-public (public to a group(s) of users), or private
* `dataStoreId`: Id of the storage in which the image will be stored
* `acls`: List of access control list Ids with whom the image is shared
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

`GET /images/<imageId>`

**Request Headers**:
* `Accept`: Set this header to `application/octet-stream`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body (on success)**: The image

***
### copy

Make a golden copy of source image (its Id is part of url).

`POST /images/<imageId>/copy`

**Request Body Example**:

    {
                "name": "ubuntu-1404-cassandra_new",
                "dataStoreId": 1
    }

**Parameters**:
* `name`: Name for the destination image
* `dataStoreId`: Id of the storage in which the copy image will be stored

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
* ownerUserId
* visibility
* acls

`PATCH /images/<imageId>`

**Request Body Example**:

    {
                "name": "ubuntu-1404-cassandra",
                "ownerUserId": 2,
                "visibility": 1
                "acls": [
                      1,
                      3,
                      ...
                ]
    }

**Parameters**:
* `name`: New name for the image
* `ownerUserId`: Id of the owner
* `visibility`: New visibility level of the image
* `acls`: New list of ACLs that will have access to the image

**Response body (on success)**: No Body

***
### delete

Delete an image.

`DELETE /images/<imageId>`

**Request Body**: No Body

**Parameters**:
* `imageId`: Id of the image to delete

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### add-acl

Share an image with an ACL.

`PUT /images/<imageId>/acls/<aclId>`

**Request Body**: No Body

**Parameters**:
* `imageId`: Id of the image
* `aclId`: Id of the ACL that needs to be added to the image's ACLs

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### remove-acl

Un-share an image with an ACL.

`DELETE /images/<imageId>/acls/<aclId>`

**Request Body**: No Body

**Parameters**:
* `imageId`: Id of the image
* `aclId`: Id of the ACL with whom the image won't be shared anymore

**Authorization**: User/Admin

**Response (on success)**: No Body

***
### list

List user's images (and snapshots). In case of admin, all images (and snapshots) will be listed.

`GET /images`

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
### show

Show details of an image.

`GET  /images/<imageId>`

**Request Headers**:
* `Accept`: Set this to `application/json`

**Request Body**: No Body

**Authorization**: User/Admin

**Response body Example (on success)**:

    {
                "imageName": "ubuntu-1404",
                "ownerUserId": 123,
                "type": "crow",
                "visibility": 0,
                "isSnapshot": 0,
                "dataStoreId": 1,
                 "acls": [
                        1,
                        2
                        ...
                ]
    }

**Response Parameters**:
* `name`: Name of the image
* `ownerUserId`: User Id of the image's owner
* `type`: Type of image that could be crow, etc
* `visibility`: Visibility of the image that could be public, semi-public (public to a group(s) of users), or private
* `isSnapshot`: Whether the image is snapshot or not
* `dataStoreId`: Id of the storage in which the image will be stored
* `acls`: List of ACLs with whom the image is shared

## Authentication
### create

Register an authentication server.

`POST /authentications`

**Request Body Example**:

    {
                "name": "auth01",
                "type": "LDAP",
                "ip": "128.11.1.1",
                "port": 22,
                "url": ""
    }

**Parameters**:
* `name`: Name of the authentication server
* `type`: Type of the authentication server
* `ip`: IP address of the authentication server
* `port`: Port of the authentication server
* `url`: URL to connect to the authentication server

**Authorization**: Admin

**Response body (on success)**:

    {
                "authenticationId": 1
    }

**Response Parameters**:
* `authenticationId`: Unique Id of the authentication server

***
### update

Update attributes of an authentication server.

**Supported Attributes**
* name
* ip
* port
* url

`PATCH /authentications/<authenticationId>`

**Authorization**: Admin

**Request Body Example**:

    {
                "name": "auth01",
                "ip": "128.11.1.1",
                "port": 22,
                "url":      
    }

**Parameters**:
* `name`: Name of the authentication server
* `ip`: IP address of the authentication server
* `port`: Port of the authentication server
* `url`: URL to connect to the authentication server

**Response body (on success)**: No Body

***
### delete

De-register an authentication server.

`DELETE /authentications/<authenticationId>`

**Request Body**: No Body

**Parameters**:
* `authenticationId`: Id of the authentication server to delete

**Authorization**: Admin

**Response (on success)**: No Body

### list  

List all authentication servers.

`GET /authentications`

**Request Body**: No Body

**Authorization**: User/Admin

**Response (on success)**:

    {
                "authentications": [
                    { "id":1, "name":"auth01"},
                    ...
                ]
    }

**Response Parameters**:
* `authentications`: List of all registered authentication servers.

***
### show

Show details of an authentication server.

`GET /authentications/<authenticationId>`

**Request Body**: No Body

**Parameters**:
* `authenticationId`: Id of the authentication server whose attributes will be shown

**Authorization**: Admin
* A non-admin user can only call this API to see the details of the authentication server that he/she uses.

**Response (on success)**:

    {
                "name": "auth01",
                "type": "LDAP",
                "ip": "128.11.1.1",
                "port": 22,
                "url": ""
    }

**Response Parameters**:
* `name`: Name of the authentication server
* `type`: Type of the authentication server
* `ip`: IP address of the authentication server
* `port`: Port of the authentication server
* `url`: URL to connect to the authentication server

## DataStore
### create

Register a data store.

`POST /dataStores`

**Request Body Example**:

    {
                "name": "dataStore01",
                "type": "Ceph",
                "ip": "225.1.1.1",
                "port": 22,
                "url": ""
    }

**Parameters**:
* `name`: Name of the data store
* `type`: Type of the data store
* `ip`: IP address of the data store
* `port`: Port of the data store
* `url`: URL to connect to the data store

**Authorization**: Admin

**Response body (on success)**:

    {
                "dataStoreId": 1
    }

**Response Parameters**:
* `dataStoreId`: Unique Id of the data store.

***
### update

Update attributes of a data store.

**Supported Attributes**
* name
* ip
* port
* url

`PATCH /dataStores/<dataStoreId>`

**Authorization**: Admin

**Request Body Example**:

    {
                "name": "dataStore01",
                "ip": "225.10.1.1",
                "port": 22,
                "url": ""   
    }

**Parameters**:
* `name`: Name of the data store.
* `ip`: IP address of the data store.
* `port`: Port of the data store.
* `url`: URL to connect to the data store.

**Response body (on success)**: No Body

***
### delete

De-register a data store.

`DELETE /dataStores/<dataStoreId>`

**Request Body**: No Body

**Parameters**:
* `dataStoreId`: Id of the data store to delete

**Authorization**: Admin

**Response (on success)**: No Body

### list  

List all registered data stores.

`GET /dataStoress`

**Request Body**: No Body

**Authorization**: User/Admin

**Response (on success)**:

    {
                "dataStoress": [
                    { "id":1, "name":"dataStore01"},
                    ...
                ]
    }

**Response Parameters**:
* `dataStores`: List of all data stores.

***
### show

Show details of a data store.

`GET dataStores/<dataStoreId>`

**Request Body**: No Body

**Parameters**:
* `dataStoreId`: Id of the data store

**Authorization**: Admin
* A non-admin user can only call this API for the dataStore on which his/her images is stored.

**Response (on success)**:

    {
                "name": "dataStore01",
                "type": "ceph",
                "ip": "225.10.1.1",
                "port": 22,
                "url": ""
    }

**Response Parameters**:
* `name`: Name of the data store
* `type`: Type of the data store
* `ip`: IP address of the data store
* `port`: Port of the data store
* `url`: URL to connect to the data store

## VLAN
### create

Register a vlan.

`POST /vlans`

**Request Body Example**:

    {
                "number": 100
    }

**Parameters**:
* `number`: VLAN number

**Authorization**: Admin

**Response body (on success)**:

    {
                "vlanId": 1
    }

**Response Parameters**:
* `vlanId`: Unique Id of the registered VLAN.

***
### delete

De-Register a VLAN.

`DELETE /vlans/<vlanId>`

**Request Body**: No Body

**Parameters**:
* `vlanId`: Id of the vlan to delete

**Authorization**: Admin

**Response (on success)**: No Body

***
### list  

View list of all VLANs.

`GET /vlans`

**Request Body**: No Body

**Authorization**: Admin

**Response (on success)**:

    {
                "vlans": [
                    { "id":1, "name":"vlan01"},
                    ...
                ]
    }

**Response Parameters**:
* `vlans`: List of VLANs

***
### show

Show details of a VLAN.

`GET /vlans/<vlanId>`

**Request Body**: No Body

**Parameters**:
* `vlanId`: Id of the VLAN

**Authorization**: Admin

**Response (on success)**:

    {
                "number": 100
    }

**Response Parameters**:
* `number`: VLAN number


## ProvisionEngine
### create

Register a provision engine.

`POST /provisionEngines`

**Request Body Example**:

    {
                "name": "provEng01",
                "type": "iscsi",
                "ip": "225.1.1.1",
                "port": 22,
                "url": ""
    }

**Parameters**:
* `name`: Name of the provision engine
* `type`: Type of the provision engine
* `ip`: IP address of the provision engine
* `port`: Port of the provision engine to connect to it
* `url`: URL to connect to the provision engine

**Authorization**: Admin

**Response body (on success)**:

    {
                "provisionEngineId": 1
    }

**Response Parameters**:
* `provisionEngineId`: Unique Id of the provision engine

***
### update

Update attributes of a provision engine.

**Supported Attributes**
* name
* ip
* port
* url

`PATCH /provisionEngines/<provisionEngineId>`

**Request Body Example**:

    {
                "name": "provEng01",
                "ip": "225.10.1.1",
                "port": 22,
                "url":  ""    
    }

**Parameters**:
* `name`: Name of the provision engine
* `ip`: IP address of the provision engine
* `port`: Port of the provision engine
* `url`: URL to connect to the provision engine

**Authorization**: Admin

**Response body (on success)**: No Body

***
### delete

De-Register a provision engine.

`DELETE /provisionEngines/<provisionEngineId>`

**Request Body**: No Body

**Parameters**:
* `provisionEngineId`: Id of the provision engine to delete

**Authorization**: Admin

**Response (on success)**: No Body

### list  

List all registered provision engines.

`GET /provisionEngines`

**Request Body**: No Body

**Authorization**: User/Admin

**Response (on success)**:

    {
                "provisionEngines": [
                    { "id":1, "name":"provEng01"},
                    ...
                ]
    }

**Response Parameters**:
* `provisionEngines`: List of all provision engines

***
### show

Show details of a provision engine.

`GET /provisionEngines/<provisionEngineId>`

**Request Body**: No Body

**Parameters**:
* `provisionEngineId`: Id of the provision engine that the node uses

**Authorization**: Admin

**Response (on success)**:

    {
                "name": "provEng01",
                "type": "iscsi",
                "ip": "225.10.1.1",
                "port": 22,
                "url": ""
    }

**Response Parameters**:
* `name`: Name of the provision engine
* `type`: Type of the provision engine
* `ip`: IP address of the provision engine
* `port`: Port of the provision engine to connect to it
* `url`: URL to connect to the provision engine

***
### add-vlan-interface

Register provision engine's network interface to VLAN mapping.

`PUT /provisionEngines/<provisionEngineId>/vlans/<vlanId>`

**Request Body Example**:

    {
                "interfaceName": "eth01"
    }

**Parameters**:
* `provisionEngineId`: Id of the provision engine
* `vlanId`: Id of the VLAN
* `interfaceName`: Name of the network interface on the provision engine

**Authorization**: Admin

**Response body (on success)**: No Body

***
### remove-vlan-interface

De-register provision engine's network interface to VLAN mapping.

`DELETE /provisionEngines/<provisionEngineId>/vlans/<vlanId>`

**Request Body**: No Body

**Parameters**:
* `provisionEngineId`: Id of the provision engine
* `vlanId`: Id of the VLAN

**Authorization**: Admin

**Response body**: No Body

***
### list-vlan-interface

List provision engine's network interface to VLAN mappings.

`GET /provisionEngines/<provisionEngineId>/vlans`

**Request Body**: No Body

**Parameters**:
* `provisionEngineId`: Id of the provision engine

**Authorization**: Admin

**Response body (on success)**:

{
            "provisionEngineVlans": [
                { "id":1, "vlanId": 100, "interfaceName": "eth01"},
                ...
            ]
}

**Response Parameters**:
* `provisionEngineVlans`: List of VLAN-Interface mapping for the given provisionEngineId
