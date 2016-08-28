import zmq
import time
import sys
import os
import curl
import json

port = "53229"

cur_dir = "/home/savi/zeromq/test1"
os.chdir(cur_dir)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://0.0.0.0:%s" % port)

file_num = 0

while True:
    #  Wait for next request from client
    file_name = "pii_sniff_%s.json" % file_num
    message = socket.recv()
    print "SENDING file %d to Savi VM" % file_num
    message1 = json.loads(message)
    #print message1
    for elem in message1:
        if "id" in elem.keys():
            id_num = elem["id"]
            print elem
            message1.remove(elem)

    message2 = json.dumps(message1, indent=4)
    #socket.send("ID "+str(id_num)+"  RECEIVED SUCCESSFULLY ---> SENDING "+ str(file_name) +" to SAVI\n")
    curl.create_file(file_name, message2, db=True)
    socket.send("ID "+str(id_num)+"  RECEIVED SUCCESSFULLY ---> SENDING "+ str(file_name) +" to SAVI\n")
    #socket.send("RECEIVED MESSSAGE")
    time.sleep(2)
    file_num += 1
