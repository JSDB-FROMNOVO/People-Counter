import monitor_mode
import time

def run():
    monitor_mode.start()
    time.sleep(10)
    monitor_mode.stop()
