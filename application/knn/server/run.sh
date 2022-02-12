#!/bin/bash

sudo killall python3
for port in {10001..10020}
do
	python3 server_knn_reporting.py -H 10.50.0.6 -P $port -T $1 &
done


