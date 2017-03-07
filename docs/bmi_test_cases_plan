BMI test cases
For now, we have BMI rest API
Commands:
  cp        Copy an existing image not clones
  db        DB Related Commands
  download  Download Image from BMI
  dpro      Deprovision a node
  export    Export a BMI image to ceph
  import    Import an Image or Snapshot into BMI
  iscsi     ISCSI Related Commands
  ls        List Images Stored
  mv        Move Image From Project to Another
  node      Node Related Commands
  pro       Provision a Node
  project   Project Related Commands
  rm        Remove an Image
  showpro   Lists Provisioned Nodes
  snap      Snapshot Related Commands
  upload    Upload Image to BMI

We design test cases based on APIs we have. 

1. cp
bmi cp [OPTIONS] SRC_PROJECT IMG1 DEST_PROJECT IMG2

2. db
bmi db create [OPTIONS] PROJECT IMG
bmi db ls
bmi db rm [OPTIONS] PROJECT IMG

3. download
Not Yet Implemented

4. drpo:
bmi dpro [OPTIONS] PROJECT NODE NETWORK NIC

5. export
bmi export [OPTIONS] PROJECT IMG NAME

6. import
bmi import [OPTIONS] PROJECT IMG

7. iscsi  (need to reimplement)
bmi iscsi create [OPTIONS] PROJECT IMG
bmi iscsi ls [OPTIONS] PROJECT
bmi iscsi rm [OPTIONS] PROJECT IMG

8. ls
bmi ls [OPTIONS] PROJECT

9. mv
bmi mv [OPTIONS] SRC_PROJECT IMG1 DEST_PROJECT IMG2

10. node
bmi node ip [OPTIONS] PROJECT NODE

11. pro:
bmi pro [OPTIONS] PROJECT NODE IMG NETWORK NIC

12. bmi project
bmi project create [OPTIONS] PROJECT NETWORK
bmi project ls
bmi project rm [OPTIONS] PROJECT

13. rm
bmi rm [OPTIONS] PROJECT IMG

14. showpro
bmi showpro [OPTIONS] PROJECT

15. snap
bmi snap create [OPTIONS] PROJECT NODE SNAP_NAME
bmi snap ls [OPTIONS] PROJECT
bmi snap rm [OPTIONS] PROJECT SNAP_NAME

16. upload
Not Yet Implemented
