#!/bin/bash
PHY_IFACE=`sudo iw dev | grep mon0 -B1 | head -n1 | sed 's/#//g'`

sudo ifconfig mon0 down
sudo iw phy $PHY_IFACE interface add wlan0 type managed 
sudo iw dev mon0 del
iw dev
iwconfig wlan0
sudo ifdown wlan0
sleep 5
sudo ifup wlan0
