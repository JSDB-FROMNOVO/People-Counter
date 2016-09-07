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

cur_dir = '/home/ubuntu/ugradproject/pythonserver/test2'
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

def add_sniff(sniff, onion_num):
    """ add sniff to collection based 
        on if vendor exists 
    """
    mac = sniff["source"]
    db = None
    #sniff_type = get_sniff_type(sniff)
    if check_if_real_mac(mac):
        sniff["vendor"] = check_if_real_mac(mac)
        if onion_num == 1:
	    db = mongo.db.real_sniffs_onion1
	elif onion_num == 2:
	    db = mongo.db.real_sniffs_onion2
        sniff_type = "REAL"
    else:
        sniff["vendor"] = None
	if onion_num == 1:
            db = mongo.db.invalid_sniffs_onion1
        elif onion_num == 2:
            db = mongo.db.invalid_sniffs_onion2
        sniff_type = "RANDOMIZED"

    if db.find({"source": sniff["source"]}).count() > 0:
	process_sniff(sniff, sniff_type, "update", db, onion_num)
    else:
	process_sniff(sniff, sniff_type, "add", db, onion_num)

def process_sniff(sniff, sniff_type, action, db, onion_num):
    """ returns total count collection if real or
	randomized, filters randomized sniffs based
	on tag to distinct randomized collection 
    """
     
    if onion_num == 1:
	db_invalid_sniffs = mongo.db.invalid_sniffs_onion1     
    elif onion_num == 2:
	db_invalid_sniffs = mongo.db.invalid_sniffs_onion2
    
    randomized_tag_detected = False
    if db_invalid_sniffs.find({"tags": sniff["tags"]}).count() > 0:
        randomized_tag_detected = True

    same_randomized_source = False
    #print (db_invalid_sniffs.find({"source": sniff["source"]}).count())
    if db_invalid_sniffs.find({"source": sniff["source"]}).count() > 0:
	same_randomized_source = True

    if randomized_tag_detected:
	if same_randomized_source:
	    print "True, True %f %s" % (sniff["timestamp"], str(sniff["source"]))
	else:
	    print "False, True %f %s" % (sniff["timestamp"], str(sniff["source"]))

    loc = check_detection_id(sniff, onion_num)

    #check for source as both tag and source can be the same
    if same_randomized_source:
	print "%s (%s -- %f) --> UPDATING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
        updated_sniff = update_randomized_sniff(get_source_sniff(db, sniff), sniff, loc)
        db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)	
    elif randomized_tag_detected:
        print "%s (%s -- %f) --> TAGGING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
	updated_sniff = add_randomization(get_tag_sniff(db_invalid_sniffs, sniff), sniff, loc)
        db.update_one({"tags": sniff["tags"]}, {"$set": updated_sniff}, upsert=False)
    elif action == "add":
        print "%s (%s -- %f) DETECTED --> ADDING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
        sniff = update_for_front_end(sniff, sniff_type, loc) 
        db.insert_one(sniff)
    elif action == "update":	
        print "%s (%s -- %f) --> UPDATING" % (sniff_type, str(sniff["source"]), sniff["timestamp"])
    	updated_sniff = update_real_details(get_source_sniff(db, sniff), sniff, loc)
        db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)
    
def get_source_sniff(db, sniff_search):
    for sniff in db.find():
        if sniff["source"] == sniff_search["source"]:
            return sniff

def get_tag_sniff(db, sniff_search):
    for sniff in db.find():
	if sniff["tags"] == sniff_search["tags"]:
	    return sniff

def add_randomization(updated_sniff, sniff, loc):
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
    updated_sniff["timestamp"] = sniff["timestamp"]
    updated_sniff["timestamp_list"].append({"timestamp": sniff["timestamp"], "loc_id": loc})
    return updated_sniff    

def update_randomized_sniff(updated_sniff, sniff, loc):
    """ randomized sniff detected with same mac 
	update signal strength and timestamp of
	last (most recent) mac in randomized_macs
	list
    """
    updated_sniff["signal_strength"] = str(sniff["signal_strength"])
    updated_sniff["randomized_macs"][-1]["timestamp"] = sniff["timestamp"]
    updated_sniff["randomized_macs"][-1]["counter"] += 1
    updated_sniff["timestamp_list"].append({"timestamp": sniff["timestamp"], "loc_id": loc})
    updated_sniff["timestamp"] = sniff["timestamp"]
    return updated_sniff

def update_real_details(updated_sniff, sniff, loc):
    if sniff["ssid"] == "":
        ssid = "None"
    else:
        ssid = sniff["ssid"]
    updated_sniff["ssid_list"].append(ssid.encode('utf-8'))
    updated_sniff["timestamp_list"].append({"timestamp": sniff["timestamp"], "loc_id": loc})
    return updated_sniff

def update_for_front_end(sniff, sniff_type, loc):  
    if sniff_type == "REAL":
        if sniff["ssid"] == "":
            ssid = "None"
        else:
            ssid = sniff["ssid"]
        sniff["ssid_list"] = [ssid]
        sniff["vendor_list"] = [sniff["vendor"]]
        sniff["timestamp_list"] = [{"timestamp": sniff["timestamp"], "loc_id": loc}]
    elif sniff_type == "RANDOMIZED":
        sniff["randomized_macs"] = [{
	   "mac": str(sniff["source"]),
	   "timestamp": str(sniff["timestamp"]),
	   "counter": 0
	}]
	sniff["timestamp_list"] = [{"timestamp": sniff["timestamp"], "loc_id": loc}]
    return sniff

def check_detection_id(sniff, onion_num):
    """ checks for mac within +/-15 min in other
	onion since detection in cur onion for
	intersection 
     """
    timestamp = sniff["timestamp"]
    ts_low = timestamp - 900
    ts_high = timestamp + 900

    if onion_num == 1:
	for snf in mongo.db.onion2_corrected.find({"source": sniff["source"]}):
	    if snf["timestamp"] >= ts_low and snf["timestamp"] <= ts_high: 
		return "2"
	return "0"

    if onion_num == 2:
        for snf in mongo.db.onion1_corrected.find({"source": sniff["source"]}):
            if snf["timestamp"] >= ts_low and snf["timestamp"] <= ts_high:
                return "2"
        return "1"
	
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
    real_count = mongo.db.real_sniffs_onion1.count() + mongo.db.real_sniffs_onion2.count()
    invalid_count = mongo.db.invalid_sniffs.count() + mongo.db.real_sniffs_onion2.count()
    total_count = real_count + invalid_count	
   
    count_details = {
        "total_count": total_count,
        "real_count": real_count,
        "invalid_count": invalid_count
    } 
   
    return count_details

def get_ssid_stats():
    ssid_stats = {}
    for sniff in mongo.db.real_sniffs_onion1.find():
	ssid_stats = parse_ssid(sniff, ssid_stats)
    for sniff in mongo.db.invalid_sniffs_onion1.find():
	ssid_stats = parse_ssid(sniff, ssid_stats)
  
    for sniff in mongo.db.real_sniffs_onion2.find():
        ssid_stats = parse_ssid(sniff, ssid_stats)
    for sniff in mongo.db.invalid_sniffs_onion2.find():
        ssid_stats = parse_ssid(sniff, ssid_stats)
 
    ssid_stats_top = dict(sorted(ssid_stats.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]) 
    return ssid_stats_top

def parse_ssid(sniff, ssid_stats):
    if "ssid_list" not in sniff.keys():
            return ssid_stats
    for ssid in sniff["ssid_list"]:
        key = ssid.encode('utf-8')
        if key == "":
            key = "None"
        if key not in ssid_stats.keys():
            ssid_stats[key] = 1
        else:
            ssid_stats[key] += 1
    return ssid_stats

def get_vendor_stats():
    vendor_stats = {}
    for sniff in mongo.db.real_sniffs_onion1.find():
	vendor_stats = parse_vendor(sniff, vendor_stats)
    for sniff in mongo.db.real_sniff_onion2.find():
	vendor_stats = parse_vendor(sniff, vendro_stats)

    vendor_stats_top = dict(sorted(vendor_stats.iteritems(), key=operator.itemgetter(1), reverse=True)[:5])	
    return vendor_stats_top

def parse_vendor(sniff, vendor_stats):
    if "vendor_list" not in sniff.keys():
           return vednor_stats
    for vendor in sniff["vendor_list"]:
        key = vendor.encode('utf-8')
        if vendor not in vendor_stats.keys():
            vendor_stats[key] = 1
        else:
            vendor_stats[key] += 1
    return vendor_stats

def get_sig_str_stats():
    sig_str_stats = {
	"onion1": {"strong": 0, "good": 0, "fair": 0, "poor": 0},
	"onion2": {"strong": 0, "good": 0, "fair": 0, "poor": 0}
    }
    for sniff in mongo.db.real_sniffs_onion1.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats, 1) 
    for sniff in mongo.db.invalid_sniffs_onion1.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats, 1)

    for sniff in mongo.db.real_sniffs_onion2.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats, 2) 
    for sniff in mongo.db.invalid_sniffs_onion2.find():
        sig_str_stats = process_sig_str(sniff, sig_str_stats, 2) 

    return sig_str_stats

def process_sig_str(sniff, sig_str_stats, onion_num):
    if onion_num == 1:
	stats = sig_str_stats["onion1"]
    elif onion_num ==  2:
	stats = sig_str_stats["onion2"]

    ss = sniff["signal_strength"]
    if ss >= -35: #5m
        stats["strong"] += 1
    elif ss < -35 and ss >= -45: #25m
        stats["good"] += 1
    elif ss < -45 and ss >= -49: #100m
        stats["fair"] += 1
    else: #200-250m
        stats["poor"] += 1 
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
    #onion1_start_epoch = correct_timestamp(start_epoch)
    #onion1_end_epoch = correct_timestamp(end_epoch)
   
    for sniff in mongo.db.onion1_corrected.find( { "timestamp" : { "$gt": start_epoch, "$lt": end_epoch } } ):
	del sniff['_id']
	sniffs["onion1"].append(sniff)
	sniffs["zcounter1"] += 1
    
    for sniff in mongo.db.onion2_corrected.find( { "timestamp" : { "$gt": start_epoch, "$lt": end_epoch } } ):
        del sniff['_id']
        sniffs["onion2"].append(sniff)
        sniffs["zcounter2"] += 1
    
    #for sniff in mongo.db.onion2.find():
    return sniffs

def remove_invalid(timestamp, onion_num):
    TIMECHECK = float(timestamp) - 600

    if onion_num == 1:
	db_real = mongo.db.real_sniffs_onion1
	db_invalid = mongo.db.invalid_sniffs_onion1
    elif onion_num == 2: 
        db_real = mongo.db.real_sniffs_onion2
        db_invalid = mongo.db.invalid_sniffs_onion2

    if int(timestamp) % 60 != 0:
	return
    for sniff in db_real.find( { "timestamp" : { "$lt": TIMECHECK } }):
	db_real.delete_one(sniff)
	print "REMOVING REAL %s" % str(sniff["timestamp"])
    for sniff in db_invalid.find():
	if float(sniff["randomized_macs"][-1]["timestamp"]) < TIMECHECK:
            db_invalid.delete_one(sniff)
            print "REMOVING RANDOMIZED %s" % str(sniff["timestamp"])
    #mongo.db.invalid_sniffs.deleteMany( { "timestamp": { "$lt": TIMECHECK } } )

def get_lifecycles():
    lifecycles = {}
    for sniff in mongo.db.real_sniffs_onion1.find():
	lifecycles = parse_lifecycle(sniff, lifecycles)
    for sniff in mongo.db.invalid_sniffs_onion1.find():
        lifecycles = parse_lifecycle(sniff, lifecycles)

    for sniff in mongo.db.real_sniffs_onion2.find():
        lifecycles = parse_lifecycle(sniff, lifecycles)
    for sniff in mongo.db.invalid_sniffs_onion2.find():
        lifecycles = parse_lifecycle(sniff, lifecycles)

    return lifecycles

def parse_lifecycle(sniff, lifecycles):
    if len(sniff["timestamp_list"]) == 1:
        lifecycles[sniff["source"]] = 0
    else:
        lcycle = float(sniff["timestamp_list"][-1]["timestamp"]) - float(sniff["timestamp_list"][0]["timestamp"])
        lifecycles[sniff["source"]] = int(lcycle)
    return lifecycles

def get_probe_intervals():
    probe_intervals = {}
    for sniff in mongo.db.real_sniffs_onion1.find():
        probe_intervals = parse_probe(sniff, probe_intervals)
    for sniff in mongo.db.invalid_sniffs_onion1.find():
        probe_intervals = parse_probe(sniff, probe_intervals)

    for sniff in mongo.db.real_sniffs_onion2.find():
        probe_intervals = parse_probe(sniff, probe_intervals)
    for sniff in mongo.db.invalid_sniffs_onion2.find():
        probe_intervals = parse_probe(sniff, probe_intervals)

    return probe_intervals

def parse_probe(sniff, probe_intervals):
    probe_intervals[sniff["source"]] = []
    if len(sniff["timestamp_list"]) == 1:
	probe_intervals[sniff["source"]].append(0)
    else:
	tlist_len = len(sniff["timestamp_list"]) - 1
	for i in range(tlist_len):
	    tlist = sniff["timestamp_list"]
	    pinterval = tlist[i+1]["timestamp"] - tlist[i]["timestamp"]
	    probe_intervals[sniff["source"]].append(pinterval)
    return probe_intervals 

def lifecycle_fend(lifecycles):
    output = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
    for source in lifecycles.keys():
	lcycle = math.ceil(lifecycles[source]/60)
	output[lcycle] += 1
    return output 

def lcycle_probability_fend(lifecycles):
    output = {0: None, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
    total = 0
    print lifecycles
    print lifecycles.keys()
    for time in lifecycles.keys():
	total += lifecycles[time]
    print total
    for time in lifecycles.keys():
	prob = float(lifecycles[time])/float(total)
	output[time] = round(prob, 3)
    return output 

def probe_fend(probes):
    output = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0}
    for source in probes.keys():
	for pinterval in probes[source]:
	    #consequtive bursts (<5sec) in probes
	    if pinterval < 5 and pinterval > 0:
		rnum = 4
		pinterval = round(pinterval/60, rnum)
		if pinterval > 0.002 and pinterval < 0.01:
		    rnum = 3
		    pinterval = round(pinterval, rnum)
		elif pinterval >= 0.01:
		    rnum = 2
		    pinterval = round(pinterval, rnum)
		if pinterval not in output.keys():
		    output[pinterval] = 1
		else:
		    output[pinterval] += 1
	    elif pinterval == 0 or pinterval >= 5:
		pinterval = math.ceil(pinterval/60)
		output[pinterval] += 1
    return output


""" Heatmap functions """

def getheatmap(start_time, end_time):
    hmap = {}
    start = round((start_time / 10.0)) * 10
    end = round((end_time / 10.0)) * 10
    intervals = int((end - start) / 60) + 1
    for i in range(intervals):
        t = int(start + i*60)
        hmap[t] = {"0": 0, "1": 0, "2": 0}
    return hmap

def getintervalmap(start_time, end_time):
    interval_map = {}
    start = round((start_time / 10.0)) * 10
    end = round((end_time / 10.0)) * 10  
    intervals = int((end - start) / 60) + 1
    for i in range(intervals):
        t = int(start + i*60)
        interval_map[t] = [] 
    return interval_map

def get_time_map(timestamp):
    """ round timestamp (seconds) to closest minute """
    output = round(timestamp/60)*60
    return output

def get_heatmap_stats(start_time, end_time):
    #1471687680, 1471688460
    #1471687980, 1471688760
    heatmap = getheatmap(start_time, end_time) 
    intervals_map = getintervalmap(start_time, end_time)

    for sniff in mongo.db.real_sniffs_onion1.find():
	parser = parse_sniff_loc(sniff, heatmap, intervals_map)
	heatmap = parser["heatmap"]
	intervals_map = parser["intervals_map"]
    for sniff in mongo.db.invalid_sniffs_onion1.find():
        parser = parse_sniff_loc(sniff, heatmap, intervals_map)
        heatmap = parser["heatmap"]
        intervals_map = parser["intervals_map"]

    for sniff in mongo.db.real_sniffs_onion2.find():
        parser = parse_sniff_loc(sniff, heatmap, intervals_map)
        heatmap = parser["heatmap"]
        intervals_map = parser["intervals_map"]
    for sniff in mongo.db.invalid_sniffs_onion2.find():
        parser = parse_sniff_loc(sniff, heatmap, intervals_map)
        heatmap = parser["heatmap"]
        intervals_map = parser["intervals_map"]
    #print(json.dumps(intervals_map, sort_keys=True, indent=4, separators=(',', ': ')))
    return heatmap

def parse_sniff_loc(sniff, heatmap, intervals_map):
    """ "0"-onion1, "1"-onion2, "2"-onion1and2 """
    output = {"heatmap": None, "intervals_map": None}
    for timestamp in sniff["timestamp_list"]:
        timemap = int(get_time_map(timestamp["timestamp"]))
        if sniff["source"] in intervals_map[timemap]:
            #print "cont"
	    continue
        elif timestamp["loc_id"] == "0":
            heatmap[timemap]["0"] += 1            
            intervals_map[timemap].append(sniff["source"])
	    #print ""
        elif timestamp["loc_id"] == "1":
            heatmap[timemap]["1"] += 1
            intervals_map[timemap].append(sniff["source"])
	    #print ""
        elif timestamp["loc_id"] == "2":
            heatmap[timemap]["2"] += 1
            intervals_map[timemap].append(sniff["source"])
	    #print ""
    output["heatmap"] = heatmap
    output["intervals_map"] = intervals_map
    return output 

def get_fend_heatmap(heatmap):
    heatmap_fend = {
	"onion1": {},
	"onion2": {},
	"onion1and2": {}
    }
    for timestamp in sorted(heatmap.keys()):
	heatmap_fend["onion1"][timestamp] =  heatmap[timestamp]["0"]
	heatmap_fend["onion2"][timestamp] =  heatmap[timestamp]["1"]
	heatmap_fend["onion1and2"][timestamp] = heatmap[timestamp]["2"]
    return heatmap_fend


""" Vendors functions """

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
        file_data.save(os.path.join('/home/ubuntu/ugradproject/pythonserver/test2', file_name))
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
class manilla_data_per_onion(Resource):
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

# '/manilla_new/<string:start_dt>/<string:end_dt>'
class manilla_data(Resource):
    # curl http://10.12.1.37:8101/manilla_new/2016-08-20_10:08:00.0/2016-08-20_10:21:00.0 -X GET -v
    def get(self, start_dt, end_dt):
        global vendors
        vendors = get_vendor_list()
        e1 = str_to_epoch(start_dt)
        e2 = str_to_epoch(end_dt)
        print [e1, e2]
        sniffs = get_all_sniffs(e1, e2)
        for sniff in sniffs["onion1"]:
	    add_sniff(sniff, 1)
            remove_invalid(sniff["timestamp"], 1)
        for sniff in sniffs["onion2"]:
	    add_sniff(sniff, 2)
            remove_invalid(sniff["timestamp"], 2)

# '/test/<string:data_type>'
class test_data(Resource):
    # curl http://10.12.1.37:8101/test/lifecycles -X GET -v
    # curl http://10.12.1.37:8101/test/lcycle_probability -X GET -v
    # curl http://10.12.1.37:8101/test/probes -X GET -v
    def get(self, data_type):
        #global vendors
        #vendors = get_vendor_list()
	if data_type == "lifecycles":
	    lcycle = get_lifecycles()
	    output = lifecycle_fend(lcycle)
	elif data_type == "lcycle_probability":
	    lcycle_raw = get_lifecycles()
	    lcycle = lifecycle_fend(lcycle_raw)
	    output = lcycle_probability_fend(lcycle)
	elif data_type == "probes":
	    probes = get_probe_intervals()
	    output = probe_fend(probes) 
	return output
	

# '/randomized_intervals'
class rintervals(Resource):
    # curl http://10.12.1.37:8101/randomized_intervals -X GET -v
    def get(self):
	randomized_sniffs = {"onion1and2910to1042": []}
	for sniff in mongo.db.invalid_sniffs.find():
	    del sniff["_id"]
	    if len(sniff["randomized_macs"]) > 1:
		randomized_sniffs["onion1and2910to1042"].append(sniff)
	return randomized_sniffs

class heatmap(Resource):
    # curl http://10.12.1.37:8101/heatmap -X GET -v
    def get(self):
    	#start_time, end_time = 1471687680, 1471688460
	start_time, end_time = 1471687980, 1471688760
	heatmap = get_heatmap_stats(start_time, end_time)
	heatmap_fend = get_fend_heatmap(heatmap)
	return heatmap_fend

api.add_resource(files, '/files/<int:db>/<string:file_name>')
api.add_resource(data, '/data/<int:db>/<string:file_name>')
api.add_resource(upload_file, '/upload/<int:db>/<string:file_name>')
api.add_resource(upload_file_onion, '/upload/<string:device>/<int:db>/<string:file_name>')
api.add_resource(db, '/db/<string:sniff_type>')
api.add_resource(db_frontend, '/db/fend/<string:data_req>')
api.add_resource(db_add_vendors, '/db/add_vendors')
api.add_resource(manilla_data_per_onion, '/manilla/<string:start_dt>/<string:end_dt>/<int:onion>')
api.add_resource(manilla_data, '/manilla_new/<string:start_dt>/<string:end_dt>')
api.add_resource(test_data, '/test/<string:data_type>')
api.add_resource(rintervals, '/randomized_intervals')
api.add_resource(heatmap, '/heatmap')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101, debug=True)
