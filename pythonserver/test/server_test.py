from flask import Flask, jsonify, Response
from flask_restful import reqparse, abort, Api, Resource, request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin 
import os, json, simplejson
from datetime import datetime
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
        dt = str(datetime.now())
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
    elif sniff_type == "RANDOMIZED_DISTINCT":
	db = mongo.db.distinct_invalid_sniffs
    elif sniff_type == "TOTAL":
	db = mongo.db.total_sniffs
    else:
        abort_if_invalid_collection(collection)

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
 
    #db_total_sniffs = mongo.db.total_sniffs   
    #db_distinct_randomized = mongo.db.distinct_invalid_sniffs
    db_invalid_sniffs = mongo.db.invalid_sniffs     

    #distinct_sniff = False
    randomized_detected = False
    if db_invalid_sniffs.find({"tags": sniff["tags"]}).count() > 0:
	#distinct_sniff = True
	randomized_detected = True
		
    if randomized_detected:
        print "%s SNIFF (%s) ALREADY DETECTED --> ADDING" % (sniff_type, str(sniff["source"]))
	updated_sniff = update_randomized_details(get_sniff(db, sniff), sniff)
	db.update_one({"tags": sniff["tags"]}, {"$set": updated_sniff}, upsert=False)
    elif action == "add":
        #db_total_sniffs.insert_one(sniff)
	sniff["ssid_list"] = []
	db.insert_one(sniff)
	#if distinct_sniff:
	#    db_distinct_randomized.insert_one(sniff)
    elif action == "update":	
    	#db_total_sniffs.update_one({"source": sniff["source"]}, {"$set": sniff}, upsert=False)	
        print "%s SNIFF (%s) ALREADY DETECTED --> UPDATING" % (sniff_type, str(sniff["source"]))
    	updated_sniff = update_ssid_details(get_sniff(db, sniff), sniff)
	db.update_one({"source": sniff["source"]}, {"$set": updated_sniff}, upsert=False)
        #if distinct_sniff:
    	#    db_distinct_randomized.update_one({"source": sniff["source"]}, {"$set": sniff}, upsert=False)
    
def get_sniff(db, sniff_search):
   for sniff in db.find():
	if sniff["tags"] == sniff_search["tags"]:
	    return sniff

def update_randomized_details(updated_sniff, sniff):
    """ stores timestamp of randomized mac to 
	mac with corresponding tag 
    """
    if "randomized_macs" not in updated_sniff.keys():
	updated_sniff["randomized_macs"] = []
    
    randomized_details = {}
    randomized_details["mac"] = sniff["source"]
    randomized_details["timestamp"] = sniff["timestamp"]
    randomized_details["server_timestamp"] = sniff["server_timestamp"]	 
    updated_sniff["randomized_macs"].append(randomized_details)
    return updated_sniff    

def update_ssid_details(updated_sniff, sniff):
    #if "ssid_list" not in updated_sniff.keys():
	#updated_sniff["ssid_list"] = []

    updated_sniff["ssid_list"].append(sniff["ssid"])
    return updated_sniff

###

""" Front end data processing """

def get_total_devices():
    real_count = mongo.db.real_sniffs.count()
    invalid_count = mongo.db.inalid_sniffs.count()
    total_count = real_count + invalid_count
    return total_count

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



""" Error cases """

def abort_if_file_doesnt_exist(file_name, file_type):
    if file_name not in all_files[file_type]:
        abort(404, message="{} doesn't exist".format(file_name))

def abort_if_file_exists(file_name, file_type):
    if file_name in all_files[file_type]:
        abort(405, message="{} already exists".format(file_name)) 

def abort_if_invalid_collection(collection):
    if collection not in mongo.db.collection_names():
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
    # curl http://10.12.1.37:8101/db/RANDOMIZED_DISTINCT -X GET -v
    # curl http://10.12.1.37:8101/db/TOTAL -X GET -v
    def get(self, data_req):
    #def get(self, sniff_type):
        """ return data requested """
        #documents = get_documents(sniff_type)
        #return jsonify({"wifi_sniffs" : documents})
	if data_req == "total_devices":
	    total_devices = get_total_devices() #10
	    return total_devices
	elif data_req == "ssid_stats":
	    ssid_stats = get_ssid_stats() #{v1: 10, v2: 22, ...}
	    return ssid_stats
	#ssid_stats = get_ssid_stats() #{strong:10, good:12, fair:923, poor:21}
	#sig_str_stats = get_sig_str() #{phone1: [10s: 3, 20s: 4, ... , 1m: 100], phone2: [...]}
	 

    def post(self, sniff_type):
	#documents = get_documents(sniff_type)
        #return jsonify({"wifi_sniffs" : documents})	
	resp = Response("")
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

api.add_resource(files, '/files/<int:db>/<string:file_name>')
api.add_resource(data, '/data/<int:db>/<string:file_name>')
api.add_resource(upload_file, '/upload/<int:db>/<string:file_name>')
#api.add_resource(db, '/db/<string:sniff_type>')
api.add_resource(db, '/db/<string:data_req>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8101, debug=True)
