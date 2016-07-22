from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
import os, json, simplejson

os.chdir('/Users/Amar/Desktop/ugradproj/pythonserver')

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('data')

""" all files """

all_files = {
    "TEXT_FILES": [],
    "JSON_FILES": [],
    "PCAP_FILES": []
}


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

def file_achive_add(file_name, file_type):
    """ """
    if os.path.isfile("_FILELIST_.json"):
        json_file = open("_FILELIST_.json", 'r')
        data = json_file.read()
        json_file.close()
        
        files = simplejson.loads(data)
        files[file_type].append(file_name)

        create_file("_FILELIST_.json", files)
    else:
        file_data = simplejson.dumps(all_files, indent=4, skipkeys=True, sort_keys=True)
        create_file("_FILELIST_.json", file_data)

def file_archive_delete(file_name, file_type):
    json_file = open("_FILELIST_.json", 'r')
    data = json_file.read()
    json_file.close()
    
    files = simplejson.loads(data)
    files[file_type].remove(file_name)
    create_file("_FILELIST_.json", files)


""" Error cases """
 


""" Resource definitions """

class files(Resource):
    def get(self):
        """ returns all files of file_type """
        return all_files

class text(Resource):
    def get(self, file_name):
        """ List of all test files 
            TODO: List specific file details
        """
        # check_if_file_does_not_exist(file_name, file_names)
        return read_file(file_name)

    def delete(self, file_name):
        """ Delete text file """
        # check_if_file_does_not_exist(file_name, file_names)
        all_files["TEXT_FILES"].remove(file_name)
        delete_file(file_name)
        file_archive_delete(file_name, "TEXT_FILES")
        return ("Deleted " + str(file_name)), 204

    def post(self, file_name):
        # check_if_file_exists(file_name, file_names)
        all_files["TEXT_FILES"].append(file_name)
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        file_achive_add(file_name, "TEXT_FILES")
        return all_files["TEXT_FILES"]

api.add_resource(files, '/files')
api.add_resource(text, '/text_file/<string:file_name>')

if __name__ == '__main__':
    app.run(debug=True)