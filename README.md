# BMI

The Bare Metal Imaging (BMI) is a core component of the Massachusetts Open Cloud and a image management system(ims) that 
(i)provisions numerous nodes as quickly as possible while preserving support for multitenancy using Hardware as a Service (HaaS) and 
(ii)introduces the image management techniques that are supported by virtual machines, with little to no impact on application performance.

Motivation:

Imagine thousands of nodes in a data center that supports a multitenant bare metal cloud. We need a central image management service that can quickly image the nodes to meet the customer’s needs. Upon completion of a customer’s project, the data center administrator should ideally be able to reallocate the resources within few minutes to use them for another customer. As of now, these techniques are in use for Virtual Machines (VMs), but not for bare metal systems. This project aims to bridge this gap by creating a service that can address the above mentioned issues.

Bare metal systems that support Infrastructure as a Service (IaaS) solutions are gaining traction in the cloud. Some of the advantages include:

    Best isolation with respect to containers or VMs
    Predictable/stable performance when compared to VMs or containers, especially on input/output (I/O) intensive workloads such as Hadoop jobs, which need predictable storage and network I/O
    Leveraging benefits of cloud services, such as economics of scale. As of now, VMs are scalable and elastic, as a customer pays for his/her usage based on resource consumption.

The main concerns of a bare metal system are the inherent slowness in provisioning the nodes and the lack of features, such as cloning, snapshotting, etc. For these reasons, IaaS is typically implemented through VMs.

This project proposes a system that includes all of the above advantages and also addresses the fast provisioning issue for a bare metal system. Using this system, we propose to provision and release hundreds of nodes as quickly as possible with little impact on application performance.
Current BMI (IMS) Architecture

![](https://github.com/CCI-MOC/ims/blob/master/Selection_003.png)

The current design consists of a pluggable architecture that exposes an API for such features as:

    map – Maps a physical node to an image
    register –Registers a node with BMI
    rm – Removes the image from library
    list – Lists the images available
    upload – Uploads the image to library

BMIS Architecture

We use Ceph as a storage back-end to save OS images. For every application we support, we have a “golden image,” which acts as a source of truth. When a user logs-in and requests a big data environment, we clone from this golden image and provision nodes using the cloned image and a PXE bootloader. Hardware as a Service (HaaS) serves as a network isolation tool through which we achieve multitenancy. HaaS provides a service for node allocation and deallocation. For more details about HaaS, please visit https://github.com/CCI-MOC/haas.

Project Team

Core Project Team

    Professor Gene Cooperman, Northeastern University 
    Apoorve Mohan, Northeastern University
    Pranay Surana, Northeastern University 
    Ravi Santosh Gudimetla, Northeastern University
    Sourabh Bollapragada, Northeastern University

Contributors

    Dr. Ata Turk, Boston University 
    Dr. Jason Hennesey, Boston University 
    Ugur Kaynar, Boston University 
    Sahil Tikale, Boston University 

Timeline

    January – April 2016: Expose an Application Programming Interface (API) for the core functionality of a bare metal imaging system, including snapshotting, cloning, etc. Performance evaluation using ceph on headnode by enabling caching and having a multi-tenant iscsi service
    April – June 2016: Develop a scheduler that could be used in conjunction with bare metal imaging for dynamic node allocation and deallocation.
    April – June 2016: Develop scripts for turn-key solutions for HPC, BigData and Openstack clusters.

Planning and Getting Involved

To get involved in this project, please send email to (MOC team-list) and/or join the #moc irc channel on freenode.
