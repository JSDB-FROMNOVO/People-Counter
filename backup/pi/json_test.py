from scapy.all import *
import json
import time
import os
import threading
import client1
#import zmq_client1_test
from struct import *

cur_dir = "/home/pi/zeromq/test1"
os.chdir(cur_dir)

counter=0
MAX_COUNTER_VAL = 5# 100
json_list = []

json_data_lock = threading.Lock()


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
        data['destination'] = destination
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

    
        json_data_lock.acquire()
        json_list.append(data)
        counter+=1
    	print counter
        if (counter == MAX_COUNTER_VAL):
            counter = 0
            #zmq_client1_test.send_json_data(json_list)       
            client1.send_json_data(json_list)       
            json_list[:] = [] #empty the list
    
        json_data_lock.release()
	    
sniff(iface='mon0', prn=packet_handler)
