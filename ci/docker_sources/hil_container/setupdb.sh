export HIL_USERNAME=haasadmin

export HIL_PASSWORD=admin1234

hil-admin run-dev-server -p 7000 &

sleep 5

hil-admin serve-networks &

sleep 5

hil-admin create-admin-user haasadmin admin1234

hil project create bmi_infra

hil node register bmi_node mock mock-host mock-user mock-pass

hil node nic register bmi_node bmi_nic aa:bb:cc:dd:ee:ff

hil network create bmi_provision bmi_infra

hil project node add bmi_infra bmi_node

hil switch register bmi_switch mock mockhost mockuser mockpass

hil port register bmi_switch gi1/0/1

hil port nic add bmi_switch gi1/0/1 bmi_node bmi_nic

hil node show bmi_node

hil network show bmi_provision
