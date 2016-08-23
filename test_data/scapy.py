from scapy.all import *

a = rdpcap("test1.pcap")

for i in range(len(a)):
    t = a[i+5].fields
    print t
    print ""
    print a[i+5].show()
    break

