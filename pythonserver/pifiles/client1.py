import zmq
import sys
import os
import time
import test

port = "53229"

context = zmq.Context()
print "Connecting to server (vCPE)..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://10.23.100.161:%s" % port)

def get_json_data(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    return data

while True:
    # Send
    test.run()
    content = 0
    sniffs = get_json_data("snifftest.json") 
    print sniffs
    # socket.send("Hello (FROM RASBERRY PI) ---> MESSAGE NUMBER " + str(contenti))
    socket.send(sniffs)
    #  Get the reply.
    message = socket.recv()
    print (message)
    time.sleep(2)

