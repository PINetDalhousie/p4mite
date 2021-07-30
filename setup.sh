#!/bin/bash

#Kill any running switch
pkill switchd

#Set environment vars
source /root/bin/set_sde.sh


cd hesam_switch/
bf-p4c hesam_switch.p4
cp_p4 hesam_switch
cd ..


#Launch the switch
$SDE/run_switchd.sh -p hesam_switch &

#Wait to it to get setup
sleep 60

#Add the ports
$SDE/run_bfshell.sh -b $SDE/port-setup.py

#Add other control info
#python /root/hesam/hesam_switch/config_table.py
