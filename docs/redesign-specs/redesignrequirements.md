## Re-design Documentation

#### Requirements

* Remove tight coupling with external services:
  - Hardware Isolation Layer (for network isolation and authentication).
  - Ceph (as image data store).
  - Software iSCSI Frameworks (TGT and IET - for diskless provisioning).


* Remove tight coupling between CLI and BMI Components (Einstein and Database).

* Enable users to replace any external components as per his requirements and resource availability (driver based model).
  - Support for hardware iSCSI servers.
  - Support for File/Sector based diskless provisioning.
  - Support for different authentication services (e.g. LDAP, Kerberos, etc.).
  - Support for different data stores (e.g. Lustre, etc).
  - Support for different network isolators.


* Support for standalone deployment i.e. on a flat network (no multi-tenancy).

* Remove RPC communication between REST API server (Picasso) and BMI Core (Einstein).

* Extend exposed functionalities - e.g. Migrate, Access Control Lists, Tags, etc.

* Database Re-design to support for multiple external services.

* Production ready code for external users (e.g. OpenNebula, Engaging-1, IBM, etc.).
