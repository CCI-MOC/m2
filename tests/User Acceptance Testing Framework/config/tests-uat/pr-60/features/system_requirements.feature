Feature: Ensuring that the environment conforms to the specifications

  Scenario: Validating the environment specifications
     #Given the operating system
     #   | linux_distribution                   |
     #   | CentOS Linux release 7.2.1511 (Core) | 
     
     #And Ceph (RBD) version
     Given Ceph (RBD) version
        | ceph_version |
        | 10.2.9       |
          
     And dnsmasq version
        | dnsmasq_version |
        | 2.66            |
          
     And Linux target framework (tgt)
        | tgt_version |
        | 1.0.63      |
           
