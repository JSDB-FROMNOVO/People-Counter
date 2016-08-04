import zmq
import sys
import os

port = "53229"

context = zmq.Context()
print "Connecting to server (VM aa3)..."
socket = context.socket(zmq.REQ)
socket.connect ("tcp://10.23.100.161:%s" % port)

while True:
    """print "Sending request ", request,"..."
    # Send 
    socket.send ("Hello (FROM VM aa4)")
    #  Get the reply.
    message = socket.recv()
    print "Received reply ", request, "[", message, "]"""
    print ("\n\n ... \n\n")

    curFile = "test.json"
    size = os.stat(curFile).st_size
    print "SENDING FILE --> File size: %s bytes" % size

    target = open(curFile, 'rb')
    file = target.read(size)
    socket.send(file)

    message = socket.recv()
    print message
    print ("\n\n ... \n\n")
    break

