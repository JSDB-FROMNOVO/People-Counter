import zmq
import sys
import os
import time
import json

port = "53229"
id_sent = 0
REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://10.20.30.40:%s" % port

context = zmq.Context(1)
#context = zmq.Context()

print "Connecting to server (vCPE)..."

client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

poll = zmq.Poller()
poll.register(client, zmq.POLLIN)

def send_json_data(data):
    global id_sent
    global socket
    global REQUEST_TIMEOUT 
    global REQUEST_RETRIES
    global poll    
        
    while REQUEST_RETRIES:
        # Send
        print id_sent
        data_num = {}
        data_num['id'] = id_sent
        data.append(data_num)

        json_data = json.dumps(data, indent=4)
    
        client.send(json_data)

        expect_reply = True
        while expect_reply:
	    socks = dict(poll.poll(REQUEST_TIMEOUT))	    
	    if socks.get(client) == zmq.POLLIN:
            reply = client.recv()
	    reply_id = reply.split()[1]
                if not reply:
                    break
                if reply_id == id_sent:
                    print("I: Server replied OK (%s)" % reply)
                    retries_left = REQUEST_RETRIES
                    expect_reply = False
                else:
                    print("E: Malformed reply from server: %s" % reply)

            else:
                print("W: No response from server, retrying…")
                # Socket is confused. Close and remove it.
                client.setsockopt(zmq.LINGER, 0)
                client.close()
                poll.unregister(client)
                retries_left -= 1
                if retries_left == 0:
                    print("E: Server seems to be offline, abandoning")
                    break
                print("I: Reconnecting and resending id (%s)" % id_sent)
                # Create new connection
                client = context.socket(zmq.REQ)
                client.connect(SERVER_ENDPOINT)
                poll.register(client, zmq.POLLIN)
                client.send(request)

        id_sent += 1




