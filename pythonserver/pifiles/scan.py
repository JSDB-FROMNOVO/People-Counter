import subprocess
import json

def scan_ssid():
	raw = subprocess.check_output(['sudo', 'iw', 'dev', 'wlan1', 'scan'])
	#os.system('sudo iw dev wlan1 scan')
	split_raw = raw.split("BSS")

	json_list = []

	for str in split_raw:
		if len(str) > 2:
			#get the SSID, signal strength, channel, and MAC
			lines = str.split("\n")
			
			found_ssid = False
			found_sigstr = False
			found_chnl = False
			found_mac = False

			ssid = ""
			sig_str = ""
			chnl = ""
			mac = ""

			mac = lines[0].strip().split(" ")[0]
			if mac.count(":")==5:
				found_mac = True

			for l in lines:
				if "SSID:" in l:
					ssid = l[6:].strip()
					found_ssid = True
				if "signal:" in l:
					sig_str = int(float(l.split(" ")[1]))
					found_sigstr = True
				if "primary channel:" in l:
					words = l.split(" ")
					chnl = int(words[len(words)-1])
					found_chnl = True

			if not (found_ssid and found_sigstr and found_chnl and found_mac):
				continue
			
			data = {}	
			data['MAC'] = mac
			data['SSID'] = ssid
			data['sig_str'] = sig_str
			data['chnl'] = chnl

			json_list.append(data)					
	
	json_data = json.dumps(json_list, indent=4)	
	print(json_data)

scan_ssid()
