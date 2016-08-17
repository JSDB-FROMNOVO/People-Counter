#!/bin/bash

sudo iw phy phy0 interface add wlan0-1 type managed 
sudo hostapd -P /home/savi/tlin/tlin.pid -B /home/savi/tlin/hostapd-test.conf
sudo ifconfig wlan0-1 192.168.0.1/24 up
