Feature: Running an end-to-end acceptance test

  Scenario: Importing/Removing Image, DB/Ceph consistency
  
     Given RBD will create an image
        | image_name     |
        | bmi-test-image |

     And BMI log line-count will be measured at the beginning
        
     When BMI will import an image
        | image_name     | project_name  | 
        | bmi-test-image | bmi_infra     |
                    
     And BMI will provision a node
        | image_name     | project_name  | network_name      | node_name  |  NIC       | 
        | bmi-test-image | bmi_infra     | bmi_network | bmi_node   | bmi_port | 
     
     Then BMI will create a snapshot of a node
        | project_name  | node_name      |  snapshot_name           |
        | bmi_infra     | bmi_node       |  bmi-test-image-snapshot |

     Then RBD will confirm the snapshot exists
        | snapshot_name           | 
        | bmi-test-image-snapshot |
     
     And BMI will remove a snapshot
        | snapshot_name           | project_name  | 
        | bmi-test-image-snapshot | bmi_infra     |
           
     Then BMI will deprovision a node     
        | project_name  | network_name      | node_name  |  NIC       | 
        | bmi_infra     | bmi_network | bmi_node   | bmi_port | 
                
     And BMI will remove an image
        | image_name     | project_name  | 
        | bmi-test-image | bmi_infra     |
                
     Then RBD will confirm the removed image's clone
        | image_name     | project_name  | 
        | bmi-test-image | bmi_infra     |

     And RBD will remove the created image
        | image_name     |
        | bmi-test-image |
        
     And BMI log line-count will be measured at the end
     
     
        
