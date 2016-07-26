from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
import os

os.chdir('/Users/Amar/Desktop/ugradproj/pythonserver')

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('data')

""" Store different files """
files = {
    "text_files" : [], 
    "json_files": [], 
    "cap_files": [], 
    "pcap_files": []
 }

# def check_if_file_does_not_exist(file_name, file_type):
#     """ Check if file exists """
#     if file_name not in files[file_type]:
#         abort(404, message="{1} File {2} doesn't exist".format(file_type, file_name))

# def check_if_file_type_exists(file_type):
#     """ Check if file type exists """
#     if file_type not in files.keys():
#         print "{1} doesn't exist in {2}".format(file_type, file_types) 
#         abort(405, message="{1} File Type doesn't exist".format(file_type))

""" File functions """
def create_file(file_name, data):
    f = open(file_name, "w")
    f.write(data)
    f.close()

def delete_file(file_name):
    os.remove(file_name)

def read_file(file_name):
    f = open(file_name, "r")
    file_data = f.read()
    f.close()
    return file_data

# def check_if_file_exists(file_name, file_type):
#     """ Check if file exists """
#     if file_name in file_type:
#         abort(405, message="{} File {} already exist".format(file_type, file_name))

class files(Resource):
    def get(self):
        """ returns all files of file_type """
        return jsonify(files)

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
        delete_file(file_name)
        # files["text_files"].remove(file_name)
        return ("Deleted " + str(file_name)), 204

    def post(self, file_name):
        # check_if_file_exists(file_name, file_names)
        # files['text_files'].append(file_name + ".txt")
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        return str(files)
        # return read_file(file_name)

api.add_resource(files, '/files')
api.add_resource(text, '/text_file/<string:file_name>')

if __name__ == '__main__':
    app.run(debug=True)