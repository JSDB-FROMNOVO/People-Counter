#!/bin/bash
PHY_IFACE=`sudo iw dev | grep mon1 -B1 | head -n1 | sed 's/#//g'`

sudo ifconfig mon1 down
sudo iw phy $PHY_IFACE interface add wlan1 type managed 
sudo iw dev mon1 del
iw dev
iwconfig wlan1
sudo ifdown wlan1
sleep 5
sudo ifup wlan1
