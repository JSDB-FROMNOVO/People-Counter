#!/bin/bash
sudo iw phy phy0 interface add mon0 type monitor
sudo iw dev wlan0 del
sudo ifconfig mon0 up
sudo iw dev mon0 set freq 2437

