import os
import json

def main():
	with open("onion1and2910to1220randomized.json") as data_file:
		output = []
		data = json.load(data_file)
		for sniff in data["onion1and2910to1220"]:
			if len(sniff["randomized_macs"]) == 1:
				continue
			else:
				rlist = sniff["randomized_macs"]
				length = len(rlist)
				for i in range(length):
					if i == length - 1:
						break
					else:
						interval = float(rlist[i+1]["timestamp"]) - float(rlist[i]["timestamp"])
						output.append(abs(interval))	
		return output				
	
print main()
