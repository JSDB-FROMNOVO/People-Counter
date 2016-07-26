#!/bin/bash
#RAND_STR=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1`
RAND_STR=`date | md5sum | fold -w 8 | head -n 1`
heat stack-create innet_firewall_$RAND_STR -f scripts/contrail_innet_firewall.yaml -P "left_vn=d1041830-6945-410a-9776-b093d0b6caca;right_vn=2f8e8a6b-375b-4950-9987-ede828b5bc84;private_instance_name=firewall-$RAND_STR"
sleep 5
#UUID=`heat stack-list | grep innet_firewall_$RAND_STR | awk '{print $2}'`
UUID=`heat output-show innet_firewall_$RAND_STR service_uuid | sed 's/\"//g'`
echo "UUID is: $UUID"
