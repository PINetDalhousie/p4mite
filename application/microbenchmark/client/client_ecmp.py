#!/usr/bin/python3

import argparse
import socket
import time
import select
import sys
from threading import Thread
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import random
import idx2numpy


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host',
					default='127.0.0.1',
					dest='host',
					help='Provide destination host. Defaults to localhost',
					type=str
					)

parser.add_argument('-P', '--port',
					default=12345,
					dest='port',
					help='Provide destination port number. Defaults to 12345',
					type=int
					)
parser.add_argument('-B', '--buffer',
					default=1024,
					dest='buffer_size',
					help='The buffer size. Defaults is 1024',
					type=int
					)
parser.add_argument('-R', '--rate',
					default=1,
					dest='rate',
					help='The transmit rate (request/sec). Defaults is 1',
					type=float
					)

parser.add_argument('-N', '--number_packets',
					default=1,
					dest='number_packets',
					help='The number of packets(requests)',
					type=int
					)

parser.add_argument('-S', '--size',
					default=1024,
					dest='data_size',
					help='The size of data in packets(requests)',
					type=int
					)
parser.add_argument('-T', '--threshold',
                    default=1,
                    dest='threshold',
                    help='The threshold for waiting/dropping a requests=',
                    type=int
                    )

args = parser.parse_args()


server_ip = args.host
server_port = args.port
# server_port = [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010,
#                10011, 10012, 10013, 10014, 10015, 10016, 10017, 10018, 10019, 10020]

# server_port = [10001]
BUFFER_SIZE = args.buffer_size
transmit_rate = args.rate
number_of_packets = args.number_packets
size = args.data_size
threshold = args.threshold
index = 0
counter_packets = 0
counter_corrects = 0
print("The host is " + server_ip)
print("The port is " + str(server_port))
print("The buffer size is " + str(BUFFER_SIZE))
print("The transmit rate is " + str(transmit_rate))
#print(str(number_of_packets) + " packets will be sent.")

lat = []
def send_test(dst_ip, dst_port, X, counter):
	x = ''
	start = time.time()
	X = str(X)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	result = -1
	chunks = [X[i:i+BUFFER_SIZE] for i in range(0, len(X), BUFFER_SIZE)]
	for chunk in chunks:
		sock.sendto(chunk.encode(),(dst_ip, dst_port))
	#sock.sendto(x.encode(),(dst_ip, dst_port))
	input1 = [sock, sys.stdin]
	while time.time()-start<threshold:
		try:
			readyInput, readyOutput, readyException = select.select (input1, [], [],0)
			for x in readyInput:
				if x == sock:
					while True:
						data = sock.recv(BUFFER_SIZE)
						result = int(data.decode())
						sock.close()
						break
		except:
			break
	end = time.time()
	if (end-start)<threshold:
		lat.append(1000*(end-start))
		print(str(1000*(end-start))[0:10] + "\t" + str(result) + "\t" + str(counter+1))
	else: sock.close()
	#lat.append(1000*(end-start))


threads = []

while True:
	time.sleep(1/transmit_rate)
	# print("Progress: " + str(100*counter_packets/number_of_packets)+"%", end="\r")
	my_dict = {'dst_ip': server_ip, 'dst_port': server_port,
				'X':size, "counter":counter_packets}
	newthread = Thread(target=send_test,kwargs=my_dict)
	newthread.start()
	threads.append(newthread)
	index += 1
	counter_packets += 1
	if counter_packets == number_of_packets: break


for t in threads:
	t.join()

lat = np.array(lat)
print("**************************************************")
#for l in lat:
#	print("lat : " + str(l))
print("avg: ", np.average(lat))
print("std: ", np.std(lat))
print("p95: ", np.percentile(lat,95))
print("p99: ", np.percentile(lat,99))
print("los: ", 100 - 100*len(lat)/(number_of_packets) )
# print("**********************")
