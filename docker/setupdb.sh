haas serve 7000 &
sleep 1
haas serve_networks &
sleep 1
haas project_create bmi_infra
haas node_register bmi_node mock mock-host mock-user mock-pass
haas node_register_nic bmi_node bmi_nic aa:bb:cc:dd:ee:ff
haas network_create_simple bmi_provision bmi_infra
haas project_connect_node bmi_infra bmi_node
haas switch_register bmi_switch mock mockhost mockuser mockpass
haas port_register bmi_switch bmi_port
haas port_connect_nic bmi_switch bmi_port bmi_node bmi_nic
haas show_node bmi_node
haas show_network bmi_provision
