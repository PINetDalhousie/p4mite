#!/bin/bash

#rm -rf results
#mkdir results

for size in 1 2 4 8 16
do
	mkdir results/$size
	for rate in 5 10 20
	do
		for iter in {1..50}
		do
			echo p4mite $iter $size $rate
			#python3 client.py -H 10.50.0.100 -S $size -N 10 -R $rate >> results/$size/$rate
			#sleep 5
		done
	done
done
#zip -r p4mite.zip results/*


rm -rf results
mkdir results

for size in 1 2 4 8 16
do
    mkdir results/$size
    for rate in 5 10 20
    do
        for iter in {1..50}
        do
            echo server $iter $size $rate
            python3 client.py -H 10.50.0.100 -S $size -N 10 -R $rate >> results_ecmp/$size/$rate
            sleep 5
        done
    done
done

zip -r server.zip results/*
