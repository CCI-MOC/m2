Feature: Ensuring that the environment conforms to the specifications

  Scenario: Validating the environment specifications
     Given the operating system
        | linux_distribution                                  |
        | Red Hat Enterprise Linux Server release 7.2 (Maipo) | 
     
     And Ceph (RBD) version
        | ceph_version   |
        | 0.94.9-9.el7cp |
          
     And dnsmasq version
        | dnsmasq_version |
        | 2.66            |
          
     And Linux target framework (tgt)
        | tgt_version |
        | 1.0.66      |
           