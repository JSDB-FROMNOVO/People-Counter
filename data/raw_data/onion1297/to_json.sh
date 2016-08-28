#!/bin/bash

pcap=".pcap"
json=".json"

for i in $( ls ); do
	if [[ $i == *".pcap" ]]
	then
		sudo python "../pcap_to_json.py" $i ${i/pcap/json}
	fi
done
