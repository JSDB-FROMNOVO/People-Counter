from flask import Flask, jsonify
from flask_restful import reqparse, abort, Api, Resource, request
from flask_json import FlaskJSON, JsonError, json_response, as_json
import os, json, simplejson

cur_dir = '/Users/Amar/Desktop/ugradproj/server/pythonserver/'
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
    if file_name not in all_files[file_type]:
        abort(404, message="{} doesn't exist".format(file_name)) 


""" Resource definitions """

# '/files/<string:file_type>/<string:file_name>'
class files(Resource):
    # curl http://10.12.1.37:8101/files/see/files
    def get(self, file_type, file_name):
        """ List of all test files """
        return all_files

    # curl http://10.12.1.37:8101/files/TEXT_FILES/test.txt -X DELETE -v
    # curl http://10.12.1.37:8101/files/JSON_FILES/test.json -X DELETE -v
    def delete(self, file_type, file_name):
        """ Delete text file """
        abort_if_file_doesnt_exist(file_name, file_type)
        delete_file(file_name)
        all_files[file_type].remove(file_name)
        return ("Deleted " + str(file_name)), 204

# '/text_files/text/<string:file_name>'
class text(Resource):
    # curl http://10.12.1.37:8101/files/text/test2.txt -X GET -v
    def get(self, file_name):
        """ Read specific text files 
            TODO: List specific file details
        """
        abort_if_file_doesnt_exist(file_name, file_type)
        return read_file(file_name)

    # curl http://10.12.1.37:8101/files/text/test2.txt -d "data=TEXTDATA" -X POST -v
    def post(self, file_name):
        args = parser.parse_args()
        data = args['data']
        create_file(file_name, data)
        all_files["TEXT_FILES"].append(file_name)
        return all_files["TEXT_FILES"]

# '/files/upload/<string:file_type>/<string:file_name>'
class upload_file(Resource):
    # curl -i -X POST -F files=@input.txt http://10.12.1.37:8101/files/upload/TEXT_FILES/test.txt
    # curl -i -X POST -F files=@sample.json http://10.12.1.37:8101/files/upload/JSON_FILES/test.json
    def post(self, file_type, file_name):
        file_data = request.files['files']
        print file_data
        file_data.save('/Users/Amar/Desktop/ugradproj/server/pythonserver/'+file_name)
        all_files[file_type].append(file_name)
        return all_files


api.add_resource(files, '/files/<string:file_type>/<string:file_name>')
api.add_resource(text, '/textfiles/<string:file_name>')
api.add_resource(upload_file, '/files/upload/<string:file_type>/<string:file_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)