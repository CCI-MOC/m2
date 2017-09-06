[![Build Status](https://travis-ci.org/CCI-MOC/ims.svg?branch=master)](https://travis-ci.org/CCI-MOC/ims)
[![Coverage Status](https://coveralls.io/repos/github/CCI-MOC/ims/badge.svg?branch=master)](https://coveralls.io/github/CCI-MOC/ims?branch=master)
# BMI


The Bare Metal Imaging (BMI) is a core component of the Massachusetts Open Cloud and an Image Management System(IMS) that
(i)provisions numerous nodes as quickly as possible while preserving support
for multitenancy using the Hardware Isolation Layer (HIL) and  (ii)introduces the
image management techniques that are supported by virtual machines, with little to no impact on application performance.

Motivation

Imagine thousands of nodes in a data center that supports a multitenant bare metal cloud. We need a central image management service that can quickly image the nodes to meet the customer’s needs. Upon completion of a customer’s project, the data center administrator should ideally be able to reallocate the resources within few minutes to use them for another customer. As of now, these techniques are in use for Virtual Machines (VMs), but not for bare metal systems. This project aims to bridge this gap by creating a service that can address the above mentioned issues.

Bare metal systems that support Infrastructure as a Service (IaaS) solutions are gaining traction in the cloud. Some of the advantages include:

    Best isolation with respect to containers or VMs
    Predictable/stable performance when compared to VMs or containers, especially on input/output (I/O) intensive workloads such as Hadoop jobs, which need predictable storage and network I/O
    Leveraging benefits of cloud services, such as economics of scale. As of now, VMs are scalable and elastic, as a customer pays for his/her usage based on resource consumption.

The main concerns of a bare metal system are the inherent slowness in provisioning the nodes and the lack of features, such as cloning, snapshotting, etc. For these reasons, IaaS is typically implemented through VMs.

This project proposes a system that includes all of the above advantages and also addresses the fast provisioning issue for a bare metal system. Using this system, we propose to provision and release hundreds of nodes as quickly as possible with little impact on application performance.
Current BMI (IMS) Architecture

![](https://github.com/CCI-MOC/ims/blob/master/Selection_003.png)


BMIS Architecture

We use Ceph as a storage back-end to save OS images. For every application we support, we have a “golden image,” which acts as a source of truth. When a user logs-in and requests a big data environment, we clone from this golden image and provision nodes using the cloned image and a PXE bootloader. Hardware Isolation Layer (HIL) serves as a network isolation tool through which we achieve multitenancy. HIL provides a service for node allocation and deallocation. For more details about HIL, please visit https://github.com/CCI-MOC/hil.

Planning and Getting Involved

To get involved in this project, please send email to (MOC team-list) and/or join the #moc irc channel on freenode.
For more information please visit our [website](https://info.massopencloud.org/blog/bare-metal-imaging/)
You can find us on [slack](https://team-bmis.slack.com/)
