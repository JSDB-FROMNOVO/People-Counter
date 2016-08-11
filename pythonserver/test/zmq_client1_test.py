import zmq
import sys
import os
import time
import json

port = "53229"
num_sent = 0
MAX_ATTEMPTS = 5

context = zmq.Context()
print "Connecting to server (vCPE)..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://10.20.30.40:%s" % port)

def send_json_data(data):
    global num_sent
    global MAX_ATTEMPTS
    global socket

    # Send
    print num_sent
    data_num = {}
    data_num['id'] = num_sent
    data.append(data_num)

    json_data = json.dumps(data, indent=4)
    
    socket.send(json_data)
    #  Get the reply.
    message = socket.recv()
    print (message)
    

    num_sent += 1
