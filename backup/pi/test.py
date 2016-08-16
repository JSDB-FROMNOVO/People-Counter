import monitor_mode
import time

def run():
    monitor_mode.start()
    time.sleep(10)
    monitor_mode.sniff()
    time.sleep(5)
    monitor_mode.stop()

run()
