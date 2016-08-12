#!/bin/bash
PHY_IFACE=`sudo iw dev | grep wlan0 -B1 | head -n1 | sed 's/#//g'`

sudo iw phy $PHY_IFACE interface add mon0 type monitor
sudo iw dev wlan0 del
sudo ifconfig mon0 up
#sudo iw dev mon0 set freq 2412 # ch 1 
sudo iw dev mon0 set freq 2437 # ch 6

#sudo python json_test.py
