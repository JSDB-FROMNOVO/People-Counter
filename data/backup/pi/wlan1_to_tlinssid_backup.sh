#!/bin/bash
sudo iwconfig wlan1 mode Managed essid 'tlinssid'
sudo dhclient wlan1 #???
