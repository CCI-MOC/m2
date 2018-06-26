## Core
Core contains the tables (quota, image, provisioned instance, and tag) that are manipulated by user. 

#### Quota
This table contains information about the user organization or project (that we called it entity).
* id: primary key.
* entityId: user organization/project identifier. 
* quota: storage allocated for user organization/project. 
* currentUsage: current amount of quota used by the user.

#### Image
This table contains information about the golden image(s) that an entity uses to provision node instance(s).
* id: primary key.
* name: entity's specified name for the image. 
* entityId: id of the entity to which the image belong. 
* type: type of the image (e.g. QCOW).
* isPublic: visibility of the image that could be public or private. 
* isSnapshot: if the image is snapshot or not. 
* creationTime: which time the image is created?
* provisionedInstanceId: id of the provisioned instance which is provisioned via this image.

#### ProvisionedInstance
This table contains information about the entity's provisioned node instance(s).
* id: primary key.
* entityId: id of the entity to which the node belong. 
* creationTime: which time the node instance is provisioned?
* type: type of provisioning that could be virtual or bare metal. 
* name: entity's specified name for the provisioned instance.
* networkdId: VLAN on which the node is provisioned. 

#### Tag
This table contains information about the checkpoints of the entity's provisioned node instance(s).
* id: primary key.
* name: entity's specified name for the tag. 
* isActive: if tag is active and can be used or not. 
* creationTime: which time the tag is created?
* provisionedInstanceId: id of the provisionedInstance from which the tag is taken. 

## Data Storage
For each type of data storage driver (e.g. ceph), there are three tables for golden images, cloned images, and snapshots that are updated by the driver.

#### Image
This table contains information about the golden images.
* id: primary key.
* imageId: id of the image in core's image table. 
* rbdName: name of the data storage driver. 
* location: address of the data storage. 
* imageName: data storage driver's specified name of the image. 

#### Clone
This table contains information about the cloned images.
* id: primary key.
* provisionedInstanceId: id of the provisionedInstance for which the cloned image is used. 
* rbdName: name of the data storage driver. 
* parentImageId: id of the golden image in the image table in data storage driver. 

#### Snapshot
This table contains information about snapshots.
* id: primary key.
* tagId: id of the tag in the tag table in core. 
* snapshotName: name of the snapshot. 
* clonedId: id of the cloned image (in clone table in data storage driver) used for provisioning.

## Provisioning Engine 
For each type of provisioning engine driver (e.g. tgt), there is one table for provisioning that is updated by the driver.

#### Target
This table stores information required for provisioning. 
* id: primary key.
* provisionedInstanceId: id of the provisioned instance in the provisionedInstance table in core. 
* nodeAddress: MAC address of the node instance. 
* nic: NIC of the node instance. 
* location: address of the provisioning engine. 
