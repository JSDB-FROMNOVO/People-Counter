import sys
import os
import time
import curl_test

cur_dir = "/Users/Amar/Desktop/ugradproj/server/pythonserver/test"
os.chdir(cur_dir)

count = 0

while True:
    print "UPLOADING FILE %d" % count
    upload_file_name = "FILE%d.json" % count
    curl_test.upload_file("pi_test.json", upload_file_name, cur_dir, db=True)
    count += 1
    time.sleep(30)

