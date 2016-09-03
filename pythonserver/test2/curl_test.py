import subprocess
import os

all_files = "curl http://0.0.0.0:8101/files/0/all"
delete = ["curl http://0.0.0.0:8101/files/0/test.txt -X DELETE -v", "curl http://0.0.0.0:8101/files/1/test.json -X DELETE -v"]
read_file = "curl http://0.0.0.0:8101/data/0/test.txt -X GET -v"
create_file = "curl http://0.0.0.0:8101/data/0/test.txt -d data='TEXTDATA' -X POST -v"
upload_file = "curl -i -X POST -F files=@input.txt http://0.0.0.0:8101/upload/1/pi.json"
show_db = "curl http://0.0.0.0:8101/db -X GET -v"

cur_dir = "/Users/Amar/Desktop/ugradproj/server/pythonserver/test2"

""" File functions """

def show_all_files():
	subprocess.call(["curl", "http://0.0.0.0:8101/files/0/all", "-v"], shell=False)

def delete_file(file_name, db=False):
	if db:
		url = "http://0.0.0.0:8101/files/1/%s" % file_name
	else:
		url = "http://0.0.0.0:8101/files/0/%s" % file_name
	
	subprocess.call(["curl", url, "-X", "DELETE", "-v"], shell=False)

def read_file(file_name):
	url = "http://0.0.0.0:8101/data/0/%s" % file_name
	subprocess.call(["curl", url, "-X", "GET", "-v"], shell=False)

def create_file(file_name, data, db=False):
	if db:
		url = "http://0.0.0.0:8101/data/1/%s" % file_name
	else:
		url = "http://0.0.0.0:8101/data/0/%s" % file_name
	
	data = "data=%s" % data
	subprocess.call(["curl", url, "-d", data, "-X", "POST", "-v"], shell=False)	

def upload_file(file_name, upload_file_name, cur_dir, db=False):
	if db:
		url = "http://0.0.0.0:8101/upload/1/%s" % upload_file_name
	else:
		url = "http://0.0.0.0:8101/upload/0/%s" % upload_file_name

	os.chdir(cur_dir)
	local_file = "files=@%s" % file_name
	subprocess.call(["curl", "-i", "-X", "POST", "-F", local_file, url], shell=False)


""" Database funtions """

def get_collection():
	url = "http://0.0.0.0:8101/db"
	subprocess.call(["curl", url, "-X", "GET", "-v"], shell=False)	

#def check_if_real_mac(mac):
#	#mac = "F0:FB:FB:01:FA:21" 
#	mac = str(mac)
#	mac_new = mac.replace(":", "%3A")
#	url = "http://api.macvendors.com/" + mac_new
#	vendor = subprocess.check_output(["curl", url, "-s"], shell=False)	
#	
#	if len(vendor):
#		return vendor
#	else:
#		return False 

# show_all_files()
# delete_file("test.txt")
# delete_file("test.json", db=True)
# read_file("test.txt")
# create_file("test.txt", "This is simple text file!")
# upload_file("pi.json", "test.json", cur_dir, db=True)

# get_collection()
#check_real_mac()
