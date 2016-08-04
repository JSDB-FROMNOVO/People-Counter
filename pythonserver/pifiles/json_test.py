from scapy.all import *
import json
import time
import os

cur_dir = "/home/pi/zeromq/test1"
os.chdir(cur_dir)

counter=0
json_list = []

def store_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close

def packet_handler(packet):
    global counter
    global json_list

    if packet.haslayer(Dot11):
        type = packet.type
        subtype = packet.subtype
	source = packet.addr2
	destination = packet.addr1
	signal_strength = -(256-ord(packet.notdecoded[-4:-3]))
	timestamp = packet.time

	ssid = "null"

	if type==0 and (subtype==4 or subtype==5 or subtype==8):
		#type is management
		#subtype is probe request, probe resposne, or beacon
		ssid = packet.info

	#create json
	data = {}
	data['type'] = type
	data['subtype'] = subtype
	data['source'] = source
	data['destination'] = destination
	data['signal_strength'] = signal_strength
	data['timestamp'] = timestamp
	if ssid!="null" and ssid!="":
	    data['ssid'] = ssid

	json_list.append(data)
	counter+=1
	if (counter == 10):
	    json_data = json.dumps(json_list, indent=4)
	    store_file("snifftest.json",json_data)
            #print(json_data)
            #print(json_list)
            #return(json_data)
	    time.sleep(5)
	    
sniff(iface='mon0', prn=packet_handler, timeout=0.5)
