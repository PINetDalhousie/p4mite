#!/bin/bash

rm -rf log
mkdir log


for rate in 2 4 6 8 10 12 14 16 18 20
do
    echo 
	python3 client_udp_multi_ports.py -H 10.50.0.100 -N 200 -R $rate > ./log/$rate.log
	sleep 5
done



