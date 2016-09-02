from flask import Flask, jsonify, Response
from flask_restful import reqparse, abort, Api, Resource, request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin 
import os, json, simplejson
import datetime
import curl_test
import math
import oui
import operator

cur_dir = '/home/ubuntu/ugradproject/pythonserver/test1'
os.chdir(cur_dir)

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "wifisniff_db"
app.config["MONGO_URI"] = "mongodb://amar:qwerty54321@ds031835.mlab.com:31835/wifisniff_db"
mongo = PyMongo(app, config_prefix="MONGO")
api = Api(app)
CORS(app)

parser = reqparse.RequestParser()
parser.add_argument('data')

""" all files """

all_files = {
    "TEXT_FILES": [],
    "JSON_FILES": [],
    "PCAP_FILES": [],
    "BASH_FILES": [],
    "PYTHON_FILES": [],
    "HTML_FILES": [],
    "JPG_FILES": []
}

MAP = {"txt": "TEXT_FILES", "json": "JSON_FILES", "pcap": "CAP_FILES", "sh": "BASH_FILES", "py": "PYTHON_FILES", "html": "HTML_FILES", "jpg": "JPG_FILES"}

def file_ext(file_name):
    extension = file_name.rsplit('.', 1)[1]
    return MAP[extension] 


""" File functions """

def create_file(file_name, data):
    """ Creates file or 
        overwrites data on existing file 
    """
    f = open(file_name, "w")
    f.write(str(data))
    f.close()

def delete_file(file_name):
    os.remove(file_name)

def read_file(file_name):
    f = open(file_name, "r")
    file_data = f.read()
    f.close()
    return file_data


""" Database funtions """
 
compute_timestamp = []

def add_json_to_db(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data) 
    
    for sniff in json_data:
        dt = str(datetime.datetime.now())
        server_timestamp = dt.split()
	sniff["server_timestamp"] = server_timestamp
        add_sniff(sniff)

def add_json_to_onion1_collection(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)
    
    for sniff in json_data:
        dt = str(datetime.datetime.now())
        server_timestamp = dt.split()
        sniff["server_timestamp"] = server_timestamp
        #add_sniff(sniff)
	delta = 51630 + 180
	sniff["timestamp"] = sniff["timestamp"] + delta	
	
	mongo.db.onion1_corrected.insert(sniff)

def add_json_to_onion2_collection(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)

    for sniff in json_data:
        dt = str(datetime.datetime.now())
        server_timestamp = dt.split()
        sniff["server_timestamp"] = server_timestamp
        #add_sniff(sniff)

        mongo.db.onion2_corrected.insert(sniff)

def rem_json_from_db(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)
    for sniffs in json_data:
        mongo.db.wifi_sniffs.delete_one(sniffs)

def get_documents(sniff_type):
    """ TODO: implement for multiple collections """
    if sniff_type == "REAL":
        db = mongo.db.real_sniffs
    elif sniff_type == "RANDOMIZED":
        db = mongo.db.invalid_sniffs
    elif sniff_type == "Onion1":
	db = mongo.db.onion1
    else:
	abort_invalid_collection(db)
    output = []
    wifi_sniff_collection = db.find()
    for sniff in wifi_sniff_collection:
        del sniff['_id']
        output.append(sniff)
    return output

###

def get_sniff_type(sniff):
    mac = sniff["source"]
    if curl_test.check_if_real_mac(mac):
        sniff["vendor"] = curl_test.check_if_real_mac(mac)
        db = mongo.db.real_sniffs
        sniff_type = "REAL"
    else:
        sniff["vendor"] = None
        db = mongo.db.invalid_sniffs
        sniff_type = "RANDOMIZED"
    return sniff_type

def add_sniff(sniff):
    """ add sniff to collection based 
        on if vendor exists 
    """
    mac = sniff["source"]
    db = None
    #sniff_type = get_sniff_type(sniff)
    if check_if_real_mac(mac):
        sniff["vendor"] = check_if_real_mac(mac)
        db = mongo.db.real_sniffs
        sniff_type = "REAL"
    else:
        sniff["vendor"] = None
        db = mongo.db.invalid_sniffs
        sniff_type = "RANDOMIZED"

    if db.find({"source": sniff["source"]}).count() > 0:
	process_sniff(sniff, sniff_type, "update", db)
    else:
	process_sniff(sniff, sniff_type, "add", db)

def process_sniff(sniff, sniff_type, action, db):
    """ returns total count collection if real or
	randomized, filters randomized sniffs based
	on tag to distinct randomized collection 
    """
 
    db_invalid_sniffs = mongo.db.invalid_sniffs     
    
    randomized_tag_detected = False
    if db_invalid_sniffs.find({"tags": sniff["tags"]}).count() > 0:
        randomized_tag_detected = True

    same_randomized_source = False
    if db_invalid_sniffs.find({"source": sniff["source"]}).count() >0:
	same_randomized_source = True

    if randomized_tag_detected:
	if same_randomized_source:
	    print "True, True %f %s" % (sniff["timestamp"], str(sniff["source"]))
	else:
	    print "False, True %f %s" % (sniff["timestamp"], str(sniff["source"]))

    #check for source as both tag and source can be the same
    if same_randomized_source:
	print "%s (%s -- %f) --> UPDATING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
        updated_sniff = update_randomized_sniff(get_source_sniff(db, sniff), sniff)
        db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)	
    elif randomized_tag_detected:
        print "%s (%s -- %f) --> TAGGING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
	updated_sniff = add_randomization(get_tag_sniff(db_invalid_sniffs, sniff), sniff)
        db.update_one({"tags": sniff["tags"]}, {"$set": updated_sniff}, upsert=False)
    elif action == "add":
        print "%s (%s -- %f) DETECTED --> ADDING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
        sniff = update_for_front_end(sniff, sniff_type) 
        db.insert_one(sniff)
    elif action == "update":	
        print "%s (%s -- %f) --> UPDATING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
    	updated_sniff = update_real_details(get_source_sniff(db, sniff), sniff)
        db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)
    
def get_source_sniff(db, sniff_search):
    for sniff in db.find():
        if sniff["source"] == sniff_search["source"]:
            return sniff

def get_tag_sniff(db, sniff_search):
    for sniff in db.find():
	if sniff["tags"] == sniff_search["tags"]:
	    return sniff

def add_randomization(updated_sniff, sniff):
    """ stores timestamp of randomized mac to 
	mac with corresponding tag and changes
	primary source to the most recent 
	radomized source 
    """  
    randomized_details = {
	   "mac": str(sniff["source"]),
	   "timestamp": str(sniff["timestamp"]),
    	   "counter": 0
    }
    updated_sniff["randomized_macs"].append(randomized_details)
    #update signal strength of first randomized for front end 
    updated_sniff["signal_strength"] = str(sniff["signal_strength"])
    #to check if same randomized mac found case in processing
    updated_sniff["source"] = sniff["source"]
    return updated_sniff    

def update_randomized_sniff(updated_sniff, sniff):
    """ randomized sniff detected with same mac 
	update signal strength and timestamp of
	last (most recent) mac in randomized_macs
	list
    """
    updated_sniff["signal_strength"] = str(sniff["signal_strength"])
    updated_sniff["randomized_macs"][-1]["timestamp"] = sniff["timestamp"]
    updated_sniff["randomized_macs"][-1]["counter"] += 1
    return updated_sniff

def update_real_details(updated_sniff, sniff):
    if sniff["ssid"] == "":
        ssid = "None"
    else:
        ssid = sniff["ssid"]
    updated_sniff["ssid_list"].append(ssid.encode('utf-8'))
    updated_sniff["timestamp_list"].append(sniff["timestamp"])
    return updated_sniff

def update_for_front_end(sniff, sniff_type):  
    if sniff_type == "REAL":
        if sniff["ssid"] == "":
            ssid = "None"
        else:
            ssid = sniff["ssid"]
        sniff["ssid_list"] = [ssid]
        sniff["vendor_list"] = [sniff["vendor"]]
        sniff["timestamp_list"] = [sniff["timestamp"]]
    elif sniff_type == "RANDOMIZED":
        sniff["randomized_macs"] = [{
	   "mac": str(sniff["source"]),
	   "timestamp": str(sniff["timestamp"]),
	   "counter": 0
	}]
    return sniff
	
### 
    
""" Front end data processing """

service_timestamp = {
    "last_update": None 
}

get_service = {
    "total_devices": None,
    "ssid": None,
    "vendor": None,
    "sig_str": None,
    "randomized_intervals": None
}

def get_latest_update():
    global service_timestamp
    return str(service_timestamp["last_update"])    

def get_total_devices():
    real_count = mongo.db.real_sniffs.count()
    invalid_count = mongo.db.invalid_sniffs.count()
    total_count = real_count + invalid_count	
   
    count_details = {
        "total_count": total_count,
        "real_count": real_count,
        "invalid_count": invalid_count
    } 
   
    return count_details

def get_ssid_stats():
    ssid_stats = {}
    for sniff in mongo.db.real_sniffs.find():
	if "ssid_list" not in sniff.keys():
            continue
        for ssid in sniff["ssid_list"]:
            key = ssid.encode('utf-8')
            if key == "":
                key = "None"
	    if key not in ssid_stats.keys():
	        ssid_stats[key] = 1
	    else:
		ssid_stats[key] += 1

    for sniff in mongo.db.invalid_sniffs.find():
        if "ssid_list" not in sniff.keys():
            continue	
        for ssid in sniff["ssid_list"]:	
            key = str(ssid)
            if key == "":
                key = "None"
	    if key not in ssid_stats.keys():
	        ssid_stats[key] = 1
	    else:
		ssid_stats[key] += 1
   
    ssid_stats_top = dict(sorted(ssid_stats.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]) 
    return ssid_stats_top

def get_vendor_stats():
    vendor_stats = {}
    for sniff in mongo.db.real_sniffs.find():
	if "vendor_list" not in sniff.keys():
	   continue
	for vendor in sniff["vendor_list"]:
	    key = vendor.encode('utf-8')
	    if vendor not in vendor_stats.keys():
		vendor_stats[key] = 1
	    else:
		vendor_stats[key] += 1

    vendor_stats_top = dict(sorted(vendor_stats.iteritems(), key=operator.itemgetter(1), reverse=True)[:5])	
    return vendor_stats_top

def get_sig_str_stats():
    sig_str_stats = {
        "strong": 0,
        "good": 0,
        "fair": 0,
        "poor": 0
    }
    for sniff in mongo.db.real_sniffs.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats)
    
    for sniff in mongo.db.invalid_sniffs.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats)
        
    return sig_str_stats

def process_sig_str(sniff, sig_str_stats):
    ss = sniff["signal_strength"]
    if ss >= -35: #5m
        sig_str_stats["strong"] += 1
    elif ss < -35 and ss >= -45: #25m
        sig_str_stats["good"] += 1
    elif ss < -45 and ss >= -49: #100m
        sig_str_stats["fair"] += 1
    else: #200-250m
        sig_str_stats["poor"] += 1 
    return sig_str_stats

#randomized_intervals = get_randomized_intervals() #{phone1: {10s: 3, 20s: 4, ... , 1m: 100}, phone2: {...}, ...}

def get_randomized_intervals():
    """ 
        returns lifecyle of each randomized 
        mac sent by each phone that is 
        randomizing macs 
    """
    #randomized_intervals = {}
    #time_intervials = {0: 0, 10: 0, 20: 0, 30: 0, 40: 0, 50: 0, 60: 0, 80: 0, 90: 0, 100: 0, 110: 0}
    randomized_intervals = {0: 0, 10: 0, 20: 0, 30: 0, 40: 0, 50: 0, 60: 0, 80: 0, 90: 0, 100: 0, 110: 0, 120: 0, 130: 0, 140: 0, 150: 0, 160: 0, 170: 0, 180: 0, 190: 0, 200: 0, 210: 0, 220: 0, 230: 0, 240: 0, 250: 0, 260: 0}
    for sniff in mongo.db.invalid_sniffs.find():
        source = sniff["source"]
	randomized_list = sniff["randomized_macs"]
        #randomized_intervals[source] = time_intervals
        #if device hasn't randomized its mac
        if len(randomized_list) == 1:
	    continue
	else:
	    total_rmacs = len(randomized_list) - 1
	    for i in range(total_rmacs):
		if i == total_rmacs:
		    break
		interval = abs(float(randomized_list[i+1]["timestamp"]) - float(randomized_list[i]["timestamp"]))
		interval = get_time_interval(int(interval))
		#randomized_intervals[source][interval] += 1	
		randomized_intervals[interval] += 1	
    return randomized_intervals        

def get_time_interval(interval):
    #round interval to nearest 10
    rounded_interval = int(math.ceil(interval / 10.0)) * 10
    if rounded_interval > 250:
	return 260
    return rounded_interval 

def update_services():
    """ 
        update all services in global get_service
        variable if get call is 5 sec > latest 
        update
    """
    global get_service

    total_devices = get_total_devices()
    ssid = get_ssid_stats()
    vendor = get_vendor_stats()
    sig_str = get_sig_str_stats()
    randomized_intervals = get_randomized_intervals()

    get_service["total_devices"] = total_devices
    get_service["ssid"] = ssid
    get_service["vendor"] = vendor
    get_service["sig_str"] = sig_str
    get_service["randomized_intervals"] = randomized_intervals 

def update_timestamp(cur_time, data_req):
    global service_timestamp
    
    #service_timestamp[data_req].append(cur_time)
    service_timestamp["last_update"] = cur_time

def get_service_data(data_req):
    global service_timestamp
    global get_service

    #update_time = service_timestamp["last_update"]
    #cur_time = datetime.datetime.now() 
    #update_interval = get_update_time(cur_time, update_time)

    #if update_interval > 5 or update_time == None:
    #	update_timestamp(cur_time, data_req)
    #	update_services()
	#data = get_service[data_req]
    #else:
        #data = get_service[data_req]

    update_services()

    return get_service

def get_update_time(cur_time, updated_time):
    """ return seconds since last service update """
    if updated_time == None:
	return None
    interval = cur_time - updated_time # datetime.timedelta(0, 8, 562000)
    output = divmod(interval.days * 86400 + interval.seconds, 60) #(minutes, seconds)
    seconds = output[0]*60 + output[1]
    return seconds


""" TOM data analysis """

def epoch_to_datetime(s):
    #return datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f') 
    return datetime.datetime.fromtimestamp(s)

def datetime_to_epoch(dt):
    epoch = (dt - datetime.datetime(1970,1,1)).total_seconds()
    return epoch

def correct_timestamp(s):
    """ corrects timestamp to be used in onion1 collection """
    delta = 51630 + 180
    correction = s - float(delta)
    return correction

def str_to_epoch(str_dt):
    dt = datetime.datetime.strptime(str_dt, "%Y-%m-%d_%H:%M:%S.%f")
    epoch = datetime_to_epoch(dt)
    return epoch

def get_all_sniffs(start_epoch, end_epoch):
    sniffs = {
	"onion1": [],
	"onion2": [],
	"zcounter1": 0,
	"zcounter2": 0
    }

    # adjust real timestamps to onion1 timestamps    
    onion1_start_epoch = correct_timestamp(start_epoch)
    onion1_end_epoch = correct_timestamp(end_epoch)
   
    for sniff in mongo.db.onion1_corrected.find( { "timestamp" : { "$gt": onion1_start_epoch, "$lt": onion1_end_epoch } } ):
	del sniff['_id']
	# get back real timestamps from onion1 timestamps
	delta = 51630 + 180
	timestamp_corrected = sniff["timestamp"] + float(delta)
	sniff["timestamp"] = timestamp_corrected 
	sniffs["onion1"].append(sniff)
	sniffs["zcounter1"] += 1
    
    for sniff in mongo.db.onion2_corrected.find( { "timestamp" : { "$gt": start_epoch, "$lt": end_epoch } } ):
        del sniff['_id']
        sniffs["onion2"].append(sniff)
        sniffs["zcounter2"] += 1
    
    #for sniff in mongo.db.onion2.find():
    return sniffs

def remove_invalid(timestamp):
    TIMECHECK = float(timestamp) - 300
    if int(timestamp) % 60 != 0:
	return
    for sniff in mongo.db.real_sniffs.find( { "timestamp" : { "$lt": TIMECHECK } }):
	mongo.db.real_sniffs.delete_one(sniff)
	print "REMOVING REAL %s" % str(sniff["timestamp"])
    for sniff in mongo.db.invalid_sniffs.find():
	if float(sniff["randomized_macs"][-1]["timestamp"]) < TIMECHECK:
            mongo.db.invalid_sniffs.delete_one(sniff)
            print "REMOVING RANDOMIZED %s" % str(sniff["timestamp"])
    #mongo.db.invalid_sniffs.deleteMany( { "timestamp": { "$lt": TIMECHECK } } )


""" Vendors function """

vendors = {}

def get_vendor_list():
    for vendor_dict in mongo.db.vendors.find():
        return vendor_dict["vendors"]

def get_vendors():
    vendor_dict = oui.parser()
    print vendor_dict
    return vendor_dict

def check_if_real_mac(mac):
    global vendors

    #mac = "F0:FB:FB:01:FA:21" 
    mac_new = str(mac.replace(":", "")[:6].upper())
    try :
	return vendors[mac_new]
    except Exception, e:
        return False


""" Error cases """

def abort_if_file_doesnt_exist(file_name, file_type):
    if file_name not in all_files[file_type]:
        abort(404, message="{} doesn't exist".format(file_name))

def abort_if_file_exists(file_name, file_type):
    if file_name in all_files[file_type]:
        abort(405, message="{} already exists".format(file_name)) 

def abort_invalid_collection(collection):
    abort(406, message="{} collection does not exist".format(collection)) 


""" Resource definitions """

# '/files/<string:file_name>'
class files(Resource):
    # curl http://10.12.1.37:8101/files/0/all
    def get(self, file_name, db):
        """ List of all test files """
        return all_files

    # curl http://10.12.1.37:8101/files/0/test.txt -X DELETE -v
    # curl http://10.12.1.37:8101/files/1/test.json -X DELETE -v
    def delete(self, file_name, db):
        """ Delete text file """
        file_type = file_ext(str(file_name))
        abort_if_file_doesnt_exist(file_name, file_type)

        if db:
            rem_json_from_db(file_name)
        
        delete_file(file_name)
        all_files[file_type].remove(file_name)
        return ("Deleted " + str(file_name))

# '/data/<string:file_name>'
class data(Resource):
    # curl http://10.12.1.37:8101/data/0/test1txt -X GET -v
    def get(self, file_name, db):
        """ Read specific text files 
            TODO: List specific file details
        """
        file_type = file_ext(str(file_name))
        abort_if_file_doesnt_exist(file_name, file_type)
        return read_file(file_name)

    # curl http://10.12.1.37:8101/data/0/test1.txt -d data="DATA" -X POST -v
    def post(self, file_name, db):
        file_type = file_ext(str(file_name))
        abort_if_file_exists(file_name, file_type)
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        all_files[file_type].append(file_name)
        
        if db:
            add_json_to_db(file_name)

        return all_files

def add_test(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)

    for sniff in json_data:
        dt = str(datetime.datetime.now())
        server_timestamp = dt.split()
        sniff["server_timestamp"] = server_timestamp
        #add_sniff(sniff)

        mongo.db.test8.insert(sniff)

# '/upload/<int:db>/<string:file_name>'
class upload_file(Resource):
    # curl -i -X POST -F files=@input.txt http://10.12.1.37:8101/upload/0/test2.txt
    # curl -i -X POST -F files=@test2.json http://10.12.1.37:8101/upload/1/test2.json
    def post(self, file_name, db):
        file_type = file_ext(str(file_name))
        abort_if_file_exists(file_name, file_type)
        file_data = request.files['files']
        file_data.save(os.path.join('/home/ubuntu/ugradproject/pythonserver/test1', file_name))
        all_files[file_type].append(file_name)
        
        #if db:
        #    add_json_to_db(file_name)
        #
        #return all_files

	if db:
	    add_test(file_name)

# '/upload/<string:device>/<int:db>/<string:file_name>'
class upload_file_onion(Resource):
    # curl -i -X POST -F files=@new_entire.json http://10.12.1.37:8101/upload/onion1/1/onion1.json
    # curl -i -X POST -F files=@new_entire.json http://10.12.1.37:8101/upload/onion2/1/onion2.json
    def post(self, file_name, device, db):
        file_type = file_ext(str(file_name))
        abort_if_file_exists(file_name, file_type)
        file_data = request.files['files']
        file_data.save(os.path.join('/home/ubuntu/ugradproject/pythonserver/test1', file_name))
        all_files[file_type].append(file_name)

        if db:
            #add_json_to_db(file_name)
	    if device == "onion1":
		add_json_to_onion1_collection(file_name)
	    elif device == "onion2":
		add_json_to_onion2_collection(file_name)

        return all_files

# '/db/<string:sniff_type>'
class db(Resource):
    # curl http://10.12.1.37:8101/db/REAL -X GET -v 
    # curl http://10.12.1.37:8101/db/RANDOMIZED -X GET -v
    def get(self, sniff_type):
        """ return database """
        documents = get_documents(sniff_type)
        return jsonify({"wifi_sniffs" : documents})
	 
    def post(self, sniff_type):	
	resp = Response("")
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

class db_frontend(Resource):
    # curl http://10.12.1.37:8101/db/fend/all -X GET -v
    def get(self, data_req):
        global service_timestamp
	global get_service
        
        data = get_service_data(data_req)
        return data 

# '/db/add_vendors'          
class db_add_vendors(Resource):  
    # curl http://10.12.1.37:8101/db/add_vendors -X GET -v
    def get(self):
	vendors = get_vendors()
	mongo.db.vendors.insert({"vendors": vendors})
	return "added vendors to db" 

# '/manilla/<string:start_dt>/<string:end_dt>/<int:onion>'
class manilla_data(Resource):
    # curl http://10.12.1.37:8101/manilla/2016-08-20_10:00:00.0/2016-08-20_10:01:00.0/1 -X GET -v
    # curl http://10.12.1.37:8101/manilla/2016-08-20_10:00:00.0/2016-08-20_10:01:00.0/2 -X GET -v
    def get(self, start_dt, end_dt, onion):
	global vendors

        vendors = get_vendor_list()
	e1 = str_to_epoch(start_dt)
	e2 = str_to_epoch(end_dt)
	print [e1, e2]
	sniffs = get_all_sniffs(e1, e2) 
	#return sniffs
	if onion == 1:
    	    for sniff in sniffs["onion1"]:
		add_sniff(sniff)
	        remove_invalid(sniff["timestamp"])
	if onion == 2:
	    for sniff in sniffs["onion2"]:
		add_sniff(sniff)
                remove_invalid(sniff["timestamp"])


# '/test/<int:test_num>'
class test_data(Resource):
    # curl http://10.12.1.37:8101/test/2 -X GET -v
    # curl http://10.12.1.37:8101/test/3 -X GET -v
    def get(self, test_num):
        global vendors
        vendors = get_vendor_list()

	for sniff in mongo.db.test8.find():
	    add_sniff(sniff)

# '/temp'
class temp(Resource):
    # curl http://10.12.1.37:8101/temp -X GET -v
    def get(self):
	randomized_sniffs = {"onion1and2910to1042": []}
	for sniff in mongo.db.invalid_sniffs.find():
	    del sniff["_id"]
	    if len(sniff["randomized_macs"]) > 1:
		randomized_sniffs["onion1and2910to1042"].append(sniff)
	return randomized_sniffs

api.add_resource(files, '/files/<int:db>/<string:file_name>')
api.add_resource(data, '/data/<int:db>/<string:file_name>')
api.add_resource(upload_file, '/upload/<int:db>/<string:file_name>')
api.add_resource(upload_file_onion, '/upload/<string:device>/<int:db>/<string:file_name>')
api.add_resource(db, '/db/<string:sniff_type>')
api.add_resource(db_frontend, '/db/fend/<string:data_req>')
api.add_resource(db_add_vendors, '/db/add_vendors')
api.add_resource(manilla_data, '/manilla/<string:start_dt>/<string:end_dt>/<int:onion>')
api.add_resource(test_data, '/test/<int:test_num>')
api.add_resource(temp, '/temp')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101, debug=True)
