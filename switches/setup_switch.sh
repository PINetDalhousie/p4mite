#!/bin/bash

echo $1
echo "${1%.*}"
echo "config_${1%.*}.py"

#Kill any running switch
pkill switchd


#Set environment vars
source /root/bin/set_sde.sh

#Compile the switch
bf-p4c $1
cp_p4 "${1%.*}"


#Launch the switch
$SDE/run_switchd.sh -p "${1%.*}" &

#Wait to it to get setup
sleep 60

#Add the ports
$SDE/run_bfshell.sh -b $SDE/port-setup.py


#Add other control info
$SDE/run_bfshell.sh -b "config_${1%.*}.py"

