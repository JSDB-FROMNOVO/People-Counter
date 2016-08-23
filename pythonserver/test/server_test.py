from flask import Flask, jsonify, Response
from flask_restful import reqparse, abort, Api, Resource, request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin 
import os, json, simplejson
import datetime
import curl_test

cur_dir = '/home/ubuntu/ugradproject/pythonserver/test'
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
    else:
	abort_invalid_collection(db)
    output = []
    wifi_sniff_collection = db.find()
    for sniff in wifi_sniff_collection:
        del sniff['_id']
        output.append(sniff)
    return output

###

def add_sniff(sniff):
    """ add sniff to collection based 
        on if vendor exists 
    """
    mac = sniff["source"]
    db = None
    if curl_test.check_if_real_mac(mac):
        sniff["vendor"] = curl_test.check_if_real_mac(mac)
        db = mongo.db.real_sniffs
	sniff_type = "REAL"
    else:
	sniff["vendor"] = None
	db = mongo.db.invalid_sniffs
        sniff_type = "RANDOMIZED"

    if db.find({"source": sniff["source"]}).count() > 0:
        print "%s SNIFF (%s) ALREADY DETECTED --> UPDATING" % (sniff_type, str(sniff["source"]))
	process_sniff(sniff, sniff_type, "update", db)
    else:
        print "%s SNIFF (%s) DETECTED --> ADDING" % (sniff_type, str(sniff["source"]))
	process_sniff(sniff, sniff_type, "add", db)

def process_sniff(sniff, sniff_type, action, db):
    """ returns total count collection if real or
	randomized, filters randomized sniffs based
	on tag to distinct randomized collection 
    """
 
    db_invalid_sniffs = mongo.db.invalid_sniffs     
    
    randomized_detected = False
    if db_invalid_sniffs.find({"tags": sniff["tags"]}).count() > 0:
        randomized_detected = True
		
    if randomized_detected:
        updated_sniff = update_randomized_details(get_invalid_sniff(db, sniff), sniff)
        db.update_one({"tags": sniff["tags"]}, {"$set": updated_sniff}, upsert=False)
    elif action == "add":
        print "%s SNIFF (%s) DETECTED --> ADDING" % (sniff_type, str(sniff["source"]))
        sniff = update_for_front_end(sniff, sniff_type) 
        db.insert_one(sniff)
    elif action == "update":	
        print "%s SNIFF (%s) --> UPDATING" % (sniff_type, str(sniff["source"]))
    	updated_sniff = update_real_details(get_real_sniff(db, sniff), sniff)
        db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)
    
def get_real_sniff(db, sniff_search):
    for sniff in db.find():
        if sniff["source"] == sniff_search["source"]:
            return sniff

def get_invalid_sniff(db, sniff_search):
    for sniff in db.find():
	if sniff["tags"] == sniff_search["tags"]:
	    return sniff

def update_randomized_details(updated_sniff, sniff):
    """ stores timestamp of randomized mac to 
	mac with corresponding tag 
    """  
    print updated_sniff
    randomized_details = {
	   "mac": str(sniff["source"]),
	   "timestamp": str(sniff["timestamp"])
    }
    updated_sniff["randomized_macs"].append(randomized_details)
    #update signal strength of first randomized for front end 
    updated_sniff["signal_strength"] = str(sniff["signal_strength"])
    return updated_sniff    

def update_real_details(updated_sniff, sniff):
    if sniff["ssid"] == "":
        ssid = "None"
    else:
        ssid = sniff["ssid"]
    updated_sniff["ssid_list"].append(str(ssid))
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
	   "timestamp": str(sniff["timestamp"])
	}]
    return sniff
	
### 
    
""" Front end data processing """

service_timestamp = {
    "total_devices": [],
    "ssid": [],
    "vendor": [],
    "sig_str": [],
    "last_update": None 
}

get_service = {
    "total_devices": None,
    "ssid": None,
    "vendor": None,
    "sig_str": None
}

def get_latest_update():
    global service_timestamp
    return str(service_timestamp["last_update"])    

def get_total_devices():
    real_count = mongo.db.real_sniffs.count()
    invalid_count = mongo.db.inalid_sniffs.count()
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
            key = str(ssid)
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
    
    return ssid_stats

def get_vendor_stats():
    vendor_stats = {}
    for sniff in mongo.db.real_sniffs.find():
	if "vendor_list" not in sniff.keys():
	   continue
	for vendor in sniff["vendor_list"]:
	    key = str(vendor)
	    if vendor not in vendor_stats.keys():
		vendor_stats[key] = 1
	    else:
		vendor_stats[key] += 1
	
    return vendor_stats

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
    if ss >= -50:
        sig_str_stats["strong"] += 1
    elif ss < -50 and ss >= -60:
        sig_str_stats["good"] += 1
    elif ss < -60 and ss >= -70:
        sig_str_stats["fair"] += 1
    else:
        sig_str_stats["poor"] += 1
    return sig_str_stats

#randomized_intervals = get_randomized_intervals() #{phone1: {10s: 3, 20s: 4, ... , 1m: 100}, phone2: {...}, ...}

def get_randomized_intervals():
    """ 
        returns lifecyle of each randomized 
        mac sent by each phone that is 
        randomizing macs 
    """
    randomized_intervals = {}
    time_intervals = {0: 0, 10: 0, 20: 0, 30: 0, 40: 0, 50: 0, 60: 0, 80: 0, 90: 0, 100: 0, 110: 0}
    for sniff in mongo.db.invalid_sniffs.find():
        source = sniff["source"]
	randomized_list = sniff["randomized_macs"]
        randomized_intervals[source] = time_intervals
        #if device hasn't randomized its mac
        if len(randomized_list) == 1:
	    continue
	else:
	    total_rmacs = len(randomized_list)
	    for i in range(total_rmacs):
		if i == total_rmacs:
		    continue
		interval = randomized_list[i+1]["timestamp"] - randomized[i]["timestamp"]
		interval = get_time_interval(int(interval))
		randomized_intervals[source][interval] += 1		
    return randomized_intervals        

def get_time_interval(interval):
    #round interval to nearest 10
    rounded_interval = int(math.ceil(interval / 10.0)) * 10
    if rounded_interval > 100:
	return 110
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

    get_service["total_devices"] = total_devices
    get_service["ssid"] = ssid
    get_service["vendor"] = vendor
    get_service["sig_str"] = sig_str

def update_timestamp(cur_time, data_req):
    global service_timestamp
    
    #service_timestamp[data_req].append(cur_time)
    service_timestamp["last_update"] = cur_time

def get_service_data(data_req):
    global service_timestamp
    global get_service

    update_time = service_timestamp["last_update"]
    cur_time = datetime.datetime.now() 
    update_interval = get_update_time(cur_time, update_time)

    if update_interval > 5 or update_time == None:
	update_timestamp(cur_time, data_req)
	update_services()
	#data = get_service[data_req]
    #else:
        #data = get_service[data_req]

    return get_service

def get_update_time(cur_time, updated_time):
    """ return seconds since last service update """
    if updated_time == None:
	return None
    interval = cur_time - updated_time # datetime.timedelta(0, 8, 562000)
    output = divmod(interval.days * 86400 + interval.seconds, 60) #(minutes, seconds)
    seconds = output[0]*60 + output[1]
    return seconds


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

# '/upload/<string:file_name>'
class upload_file(Resource):
    # curl -i -X POST -F files=@input.txt http://10.12.1.37:8101/upload/0/test2.txt
    # curl -i -X POST -F files=@pi.json http://10.12.1.37:8101/upload/1/test2.json
    def post(self, file_name, db):
        file_type = file_ext(str(file_name))
        abort_if_file_exists(file_name, file_type)
        file_data = request.files['files']
        file_data.save(os.path.join('/home/ubuntu/ugradproject/pythonserver/test', file_name))
        all_files[file_type].append(file_name)
        
        if db:
            add_json_to_db(file_name)
        
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

# '/db/fend/<string:data_req>'
class db_frontend(Resource):
    # curl http://10.12.1.37:8101/db/fend/total_devices -X GET -v 
    # curl http://10.12.1.37:8101/db/fend/vendor -X GET -v
    # curl http://10.12.1.37:8101/db/fend/ssid -X GET -v
    # curl http://10.12.1.37:8101/db/fend/sig_str -X GET -v
    # curl http://10.12.1.37:8101/db/fend/randomized_lifecycle -X GET -v
    def get(self, data_req):
        global service_timestamp
	global get_service
#	""" return data requested """
#        if data_req == "total_devices":
#            return get_total_devices() #10
#        elif data_req == "vendor":
#            return get_vendor_stats() #{v1: 10, v2: 22, ...}
#        elif data_req == "ssid":  
#            return get_ssid_stats() #{s1:10, s2:12, s:923, s:21}    
#        elif data_req == "sig_str":
#            return get_sig_str_stats() #{strong:10, good:12, fair:923, poor:21}
        
        data = get_service_data(data_req)
        print service_timestamp["last_update"]
        return data 
        #randomized_intervals = get_sig_str() #{phone1: [10s: 3, 20s: 4, ... , 1m: 100], phone2: [...]}

# '/db/test/<string:data_req>'          
class db_test(Resource):  
    def get(self, data_req):
	global service_timestamp
        global get_service
	if data_req == "randomized_lifetime":
	    return get_randomized_intervals()
	    #data = get_service_data(data_req)
	    #return data
        else:
	    print service_timestamp["last_update"]
	    update_services()
	    return get_service

api.add_resource(files, '/files/<int:db>/<string:file_name>')
api.add_resource(data, '/data/<int:db>/<string:file_name>')
api.add_resource(upload_file, '/upload/<int:db>/<string:file_name>')
api.add_resource(db, '/db/<string:sniff_type>')
api.add_resource(db_frontend, '/db/fend/<string:data_req>')
api.add_resource(db_test, '/db/test/<string:data_req>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101, debug=True)
