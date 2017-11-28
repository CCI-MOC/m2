**ASSUMPTION:** A reliable underlying technology that provides 100% availablity of the database, following are some examples of the relations between different tables. 


All the tables in the BMI database are listed bellow: 

## User 

1. An entity using BMI. 
2. Users will be registered to BMI by an admin via the API after BMI has been deployed. 

* id : Id of the user (primary key)
* name : Name of the user (unique key) 
* type : Type of user (ordinary user or admin)
* quota : Quantity of datastore disk-space allocated to a user (GB)
* status : Current status of user (e.g. active, inactive, disabled, etc.)
* autheticationId : Id of the authentication service using which a user will be verified in a multi-tenant setup. A user will specify a token (obtained from the authentication service) while invoking the REST API.

****

## AccessControlList

1. List of users who can be given access to a particular resource (currently only for images). 
2. An access control list (ACL) can be created by any user (a.k.a. the user creating the access control list will be its owner). 
3. Owner of an access control list can add/remove user from the access control list. 
4. Owner can transfer the ownership of the access control list to another user. 
5. Owner can share an access control list with another user. 
6. Owner can attach/detach an access control list (owned/shared by/to him) to a resource.
7. Shared access control lists can be modified by their owner w/o approval from the user with whom the access control list was shared with.

* id : Id of the access control list (primary key)
* name : Name of the access control list 
* ownerUserId : Id of the user who owns the ACL

**NOTE:** `(name, ownerUserId) pair is unique key.`

****

## Image/Snapshot

1. A virtual disk (a.k.a. golden image) whose clone (linked clone) is used to provision a node. 
2. Users can upload images. 
3. The user uploading the image will be the owner of the uploaded image.
4. Snapshot is a special type of image that is created by deep copying the existing state of a provisioned node's image. 
5. Image/Snapshot owner can be different from the owner of an ACL. 
6. Ownership of the image/snapshot can be transfered to another user.
7. Image/Snapshot can be shared to a set of users.
8. Image/Snapshot can be made publically available to all exisiting users.

* id : Id of the image (primary key)
* name : Name of the image
* ownerUserId : Id of the user who owns the image.
* type : Type of image (e.g. RAW, QCOW2, etc.)
* visibility : Access level of image (e.g. private, public, shared, etc.)
* isSnapshot : This flag is `true` in case of snapshot and not an uploaded image
* dataStoreId : Id of the DataStore that gives information about where this image is stored. 

**NOTE:** `(name, ownerUserId) pair is unique key.`

***

## ProvisionedNode

1. Node running an operating system from the associated clone of a parent image (aka golden image). 
2. A user can provision multiple nodes.
3. A clone (shallow or deep copy depending on the underlying data store's capabilities) of the parent image is created and used to provision a node.
4. Nodes are provisioned using a provisioning engine over a network owned by the user.
5. BMI creates an interface (physical or virtual) on the provisioning engine for the users' provisioning network.

* id : Id of the provisioned node (primary key)
* macAddress : Mac address of the provisioned node (unique key)
* parentImageId : Id of the golden image.
* cloneName :  Name of the cloned image (unique key)
* nic : NIC of the provisioned node 
* ownerUserId : Id of the user who owns the provisioned node 
* provisionEngineVlanId: Id of the provisionEngineVlan. This column represents the `(provisioning engine, vlan interface)` pair that is used to provision the given node.

***

## Tag

1. Restore points of an exisitng provisioned image created by the user in time.
2. Performance of Tag creation will depend on the data stores' capabilities.
3.  All tag must be deleted before de-provisioning. 

* id : Id of the tag (primary key)
* name : Name of the tag
* nodeId :Id of the node of which this tag is created.

***

## UserAccessControlList 

1. Mapping between access control list and user.
2. A user can be assosiated to multiple access control lists.
3. An access control list can have multiple user in it.

* id: Id of the User-AceesControlList mapping (primary key)
* ACLId : Id of the ACL.
* userId: Id of the user.

**NOTE:** `(ACLId, userId) pair is unique key.`

***

## ImageAccessControlList 

1. Mapping between access control list and image. 
2. An access control list can be attached to multiple images.
3. An image can be accessed by multple access control lists.

* id: Id of the Image-AccessControlList mapping (primary key)
* ACLId: Id of the ACL. 
* imageId : Id of the image table.

**NOTE:** `(ACLId, imageId) pair is unique key.`

***

## External Service Table (Authention/DataStore/ProvisionEngine) 

1. Authentication: A service used to authenticate the legitimacy of a user request.
2. DataStore: A filesystem service where images are stored.
3. ProvisionEngine: A service used to (de)-provision a node.

* The three above tables have `<id>` (primary key), `<name>` (unique key), `<type>`, `<url>` (unique key), `<ip>`, and `<port>`

**NOTE:** `(ip, port) pair is unique key.`

***

## Vlan 

1. This table contains the list of available VLANs in the data center.

* id : Id of network (primary key) 
* number : Vlan number (unique key)

***

## ProvisionEngineVlan 

1. Mapping between Vlan and provisioningEngine.
2. Each provisioning engine can serve multiple tenants.
3. Provisioning Engine will serve different tenants on different network interfaces (physical or virtual).
4. A provisoining engine can have interface for every possible vlan.
5. A vlan can have an interface on each provisioning engine.

* id: Id of the provisionengine-vlan mapping (primary key)
* vlanId : Id of the Vlan. 
* ProvisionEngineId : Id of the ProvisionEngine. This Id is a foriegn key to the `<ProvisionEngine>` table.
* interfaceName: Name of the interface assosciated to the vlan on the provisioning engine.

**NOTE:** `(vlanId, provisoningEngineId, interfaceName) triplet is unique key.`

***

## Examples

####  image, user

* An image can only be owned by a single user. 
* A user can own multiple images.
* Note: This owner is different from the owner of ACL. 
* The owner of an image can attach different ACLs to an image.
* Ownership of an image is transferable.

[img1, userA] (correct)

[img2, userA] (correct)

[img1, userB] (incorrect)

***

#### ACL, user

* A user may or may not belong to an ACL. (a user may belong to multiple ACLs aswell)
* The owner of an ACL can add/remove users from the the ACL.
* Ownership of an ACL is transferable.

[NEU_ACL, userB] (correct)

[NEU_ACL,userD] (correct)

[MoC_ACL, userB] (correct)

***

#### ACL, image

* An image may or may not accessed by an ACL.
* Multiple ACLs can be attached to an image.

[BU_ACL, imgA] (correct)

[BU_ACL, imgC] (correct)

[NEU_ACL, imgA] (correct)

