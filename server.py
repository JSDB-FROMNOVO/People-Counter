from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
import os, json, simplejson

cur_dir = '/Users/Amar/Desktop/ugradproj/pythonserver'
os.chdir(cur_dir)

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

""" Error cases """

def abort_if_file_doesnt_exist(file_name, file_type):
    if file_name not in all_files["file_type"]:
        abort(404, message="{} doesn't exist in {}".format(file_name, file_type)) 


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
        abort_if_file_doesnt_exist
        return read_file(file_name)

    def delete(self, file_name):
        """ Delete text file """
        abort_if_file_doesnt_exist
        delete_file(file_name)
        all_files["TEXT_FILES"].remove(file_name)
        return ("Deleted " + str(file_name)), 204

    def post(self, file_name):
        abort_if_file_doesnt_exist
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        all_files["TEXT_FILES"].append(file_name)
        return all_files["TEXT_FILES"]

class upload_file(Resource):
    # curl -i -X POST -F files=@sample.txt http://127.0.0.1:5000/files/upload/TEXT_FILES/input.txt
    # curl -i -X POST -F files=@input.txt http://127.0.0.1:5000/files/upload/TEXT_FILES/sample.txt
    def post(self, file_type, file_name):
        file_data = request.files['files']
        # f.save('/Users/Amar/Desktop/ugradproj/pythonserver/text.txt')
        print file_data
        file_data.save('/Users/Amar/Desktop/ugradproj/pythonserver/'+file_name)
        all_files[file_type].append(file_name)
        # return file_data
        return all_files


api.add_resource(files, '/files')
api.add_resource(text, '/files/text/<string:file_name>')
api.add_resource(upload_file, '/files/upload/<string:file_type>/<string:file_name>')

if __name__ == '__main__':
    app.run(debug=True)