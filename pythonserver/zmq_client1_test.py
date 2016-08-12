import zmq
import sys
import os
import time
import json

port = "53229"
id_sent = 0
REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://10.23.100.143:%s" % port
#SERVER_ENDPOINT = "tcp://192.168.0.1:%s" % port

context = zmq.Context(1)
#context = zmq.Context()

print "Connecting to server (vCPE)..."

client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)
#client.connect("tcp://10.23.100.143:%s" % port)

poll = zmq.Poller()
poll.register(client, zmq.POLLIN)

def send_json_data(data):
	global id_sent
	global client
	global REQUEST_TIMEOUT 
	global REQUEST_RETRIES
	global poll    

	data_num = {}
	data_num['id'] = id_sent
	data.append(data_num)
	json_data = json.dumps(data, indent=4)

	retries_left = REQUEST_RETRIES
	while retries_left:
		#Send
		client.send(json_data)
		expect_reply = True
		while expect_reply:
			socks = dict(poll.poll(REQUEST_TIMEOUT))
			#socks = dict(poll.poll())
			print socks	    
			if socks.get(client) == zmq.POLLIN:
			#if zmq.POLLIN:
				reply = client.recv()
				reply_id = int(reply.split()[1])
				print "REPLY ID: "+str(reply_id)+" SENT ID: "+str(id_sent)
				if not reply:
					break
				if reply_id == id_sent:
					print("I: Server replied OK (%s)" % reply)
					retries_left = REQUEST_RETRIES
					expect_reply = False
					retries_left = 0
				else:
					print("E: Malformed reply from server: %s" % reply)

			else:
				print("W: No response from server, retrying...")
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
				client.send(json_data)
	id_sent += 1




