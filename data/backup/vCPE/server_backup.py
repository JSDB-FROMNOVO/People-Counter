import zmq
import time
import sys
import os

test = ""

port = "53229"

cur_dir = "/home/savi/zeromq/test1"
os.chdir(cur_dir)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://0.0.0.0:%s" % port)

def store_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()

while True:
    #  Wait for next request from client
    message = socket.recv()
    #print "Received request: ", message
    time.sleep (1)
    store_file("pi.json", message)
    socket.send("FILE RECEIVED SUCCESSFULLY (SENT BY VM aa3)")
    break
