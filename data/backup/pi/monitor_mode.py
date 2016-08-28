import subprocess
import os

cur_dir = "/home/pi/zeromq/test1"

os.chdir(cur_dir)

def start():
    subprocess.call(["./create_mon.sh"], shell=False)

def sniff():
    subprocess.call(["sudo", "python", "json_test.py"], shell=False)

def stop():
    subprocess.call(["./delete_mon.sh"], shell=False)
