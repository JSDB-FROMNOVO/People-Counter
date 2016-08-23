import pyshark
cap = pyshark.FileCapture("test1.pcap")
print cap

print cap[0]
