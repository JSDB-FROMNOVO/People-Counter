from sys import argv
from scapy.all import *
import json

#pass in files as a comma-separated list (first argument)
#will store all the contents in a single file (second argument)

script, files, output_path = argv
file_list = files.split(",")
json_list = []

for file in file_list:
    pcap = rdpcap(file)
    for packet in pcap:
        
        if packet.haslayer(Dot11):
            type = packet.type
            subtype = packet.subtype
            source = packet.addr2
            destination = packet.addr1
            signal_strength = -(256-ord(packet.notdecoded[-4:-3]))
            timestamp = packet.time
   

            if type==0 and subtype==4:
                #type is management
                #subtype is probe request
                ssid = packet.info
                seq = (packet.SC & 0xFFF0) >> 4	
        
                #create json
                data = {}
                #data['type'] = type
                #data['subtype'] = subtype
                data['source'] = source
                #data['destination'] = destination
                data['signal_strength'] = signal_strength
                data['timestamp'] = timestamp
                data['len'] = len(packet)
                data['ssid'] = ssid	
                data['seq'] = seq

                tags = ""
                elt = packet[Dot11Elt]
                while isinstance(elt, Dot11Elt):
                    if elt.ID>0:
                        tags += str(elt.ID)
                        for n in elt.info:
                            tags += str(ord(n)) + ","
                            tags = tags[:len(tags)-1] + ":"
                    elt = elt.payload
                tags = tags[:len(tags)-1]
                data['tags'] = tags
                
                json_list.append(data)


output_file = open(output_path, 'w')
output_file.write(json.dumps(json_list, indent=4))
output_file.close()
