#!/bin/bash

for rate in {5..70..5} 
do
    echo host
	python3 client_udp_multi_ports.py -H 10.50.0.100 -N $((30*rate)) -R $rate > ./log/new_switch/$rate.log
	sleep 5
done



