#!/bin/bash

sudo iw dev mon0 del
sudo iw phy phy0 interface add wlan0 type managed 
iw dev
iwconfig wlan0
sudo ifdown wlan0
sleep 5
sudo ifup wlan0
