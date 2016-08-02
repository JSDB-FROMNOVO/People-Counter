from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
from flask_pymongo import PyMongo 
import os, json, simplejson

hello = ""

cur_dir = '/Users/Amar/Desktop/ugradproj/server/pythonserver/'
os.chdir(cur_dir)

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "wifisniff_db"
app.config["MONGO_URI"] = "mongodb://amar:qwerty54321@ds031835.mlab.com:31835/wifisniff_db"
mongo = PyMongo(app, config_prefix="MONGO")
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('data')

""" all files """

all_files = {
    "TEXT_FILES": [],
    "JSON_FILES": [],
    "CAP_FILES": []
}

MAP = {"txt": "TEXT_FILES", "json": "JSON_FILES", "cap": "CAP_FILES"}

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
 
def add_json_to_db(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)
    for sniffs in json_data:
        mongo.db.wifi_sniffs.insert(sniffs)

def rem_json_from_db(file_name):
    json_file = open(str(file_name), "r")
    data = json_file.read()
    json_file.close()
    json_data = simplejson.loads(data)
    for sniffs in json_data:
        mongo.db.wifi_sniffs.remove(sniffs)


""" Error cases """

def abort_if_file_doesnt_exist(file_name, file_type):
    if file_name not in all_files[file_type]:
        abort(404, message="{} doesn't exist".format(file_name)) 


""" Resource definitions """

# '/files/<string:file_name>'
class files(Resource):
    # curl http://10.12.1.37:8101/files/all
    def get(self, file_name):
        """ List of all test files """
        return all_files

    # curl http://10.12.1.37:8101/files/test.txt -X DELETE -v
    # curl http://10.12.1.37:8101/files/test.json -X DELETE -v
    def delete(self, file_name):
        """ Delete text file """
        file_type = file_ext(str(file_name))
        rem_json_from_db(file_name)
        abort_if_file_doesnt_exist(file_name, file_type)
        delete_file(file_name)
        all_files[file_type].remove(file_name)
        return ("Deleted " + str(file_name)), 204

# '/data/<string:file_name>'
class text(Resource):
    # curl http://10.12.1.37:8101/data/test1txt -X GET -v
    def get(self, file_name):
        """ Read specific text files 
            TODO: List specific file details
        """
        file_type = file_ext(str(file_name))
        abort_if_file_doesnt_exist(file_name, file_type)
        return read_file(file_name)

    # curl http://10.12.1.37:8101/data/test1.txt -d "data=TEXTDATA" -X POST -v
    def post(self, file_name):
        file_type = file_ext(str(file_name))
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        all_files[file_type].append(file_name)
        return all_files

# '/upload/<string:file_name>'
class upload_file(Resource):
    # curl -i -X POST -F files=@input.txt http://10.12.1.37:8101/upload/test2.txt
    # curl -i -X POST -F files=@sample.json http://10.12.1.37:8101/upload/test2.json
    def post(self, file_name):
        file_type = file_ext(str(file_name))
        file_data = request.files['files']
        file_data.save(os.path.join('/Users/Amar/Desktop/ugradproj/server/pythonserver', file_name))
        all_files[file_type].append(file_name)
        add_json_to_db(file_name)
        return all_files


# api.add_resource(files, '/files/<string:file_type>/<string:file_name>')
# api.add_resource(text, '/textfiles/<string:file_name>')
# api.add_resource(upload_file, '/files/upload/<string:file_type>/<string:file_name>')

api.add_resource(files, '/files/<string:file_name>')
api.add_resource(text, '/data/<string:file_name>')
api.add_resource(upload_file, '/upload/<string:file_name>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
