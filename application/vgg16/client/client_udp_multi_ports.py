#!/usr/bin/python3

import argparse
import socket
import time
import select
import sys
from threading import Thread
import os
import numpy as np
import random



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
					default=10,
					dest='number_packets',
					help='The number of packets(requests)',
					type=int
					)
args = parser.parse_args()


server_ip = args.host
#server_port = args.port
server_port = [10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009, 10010,
               10011, 10012, 10013, 10014, 10015, 10016, 10017, 10018, 10019, 10020]
BUFFER_SIZE = args.buffer_size
transmit_rate = args.rate
number_of_packets = args.number_packets
index = 0
counter_packets = 0
counter_corrects = 0
# print("The host is " + server_ip)
# print("The port is " + str(server_port))
# print("The buffer size is " + str(BUFFER_SIZE))
# print("The transmit rate is " + str(transmit_rate))
# print(str(number_of_packets) + " packets will be sent.")

lat = []
packet_counter = 0
def send_pic(dst_ip, dst_port, filename, counter):
	global packet_counter
	start = time.time()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# sock.connect((dst_ip, dst_port))
	f = open(filename, 'rb')
	l = f.read(BUFFER_SIZE)
	x = ''
	result = -1
	while (l):
		sock.sendto(l,(dst_ip, dst_port))
		packet_counter+=1
		l = f.read(BUFFER_SIZE)
	sock.sendto(l,(dst_ip, dst_port))
	packet_counter+=1
	f.close()
	# sock.shutdown(socket.SHUT_WR)
	input1 = [sock, sys.stdin]
	while time.time()-start < 2:
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
	if(end-start)<1:
		lat.append(1000*(end-start))
		print(str(1000*(end-start))[0:10] + "\t" + str(result) + "\t" + str(counter+1))
	#r = filename.split("/")[-2]
	# print(r)

labels = ["Cat", "Dog"]
threads = []
list_of_files = []

for label in labels:
	d = os.listdir('./PetImages/' + label)
	for i in range (2):
		x = d[i]
		list_of_files.append("./PetImages/"+label+"/"+x)

random.Random(123).shuffle(list_of_files)


while True:
	time.sleep(1/transmit_rate)
	# print("Progress: " + str(100*counter_packets/number_of_packets)+"%", end="\r")
	my_dict = {'dst_ip': server_ip, 'dst_port': server_port[counter_packets%len(server_port)],
				'filename':list_of_files[index],  "counter":counter_packets}
	newthread = Thread(target=send_pic,kwargs=my_dict)
	newthread.start()
	threads.append(newthread)
	index += 1
	counter_packets += 1
	if index == len(list_of_files): index = 0
	if counter_packets == number_of_packets: break


for t in threads:
	t.join()

lat = np.array(lat)
#print(sum(lat)/len(lat), len(lat)
print("avg: ", np.average(lat))
print("std: ", np.std(lat))
print("p95: ", np.percentile(lat,95))
print("p99: ", np.percentile(lat,99))
print("los: ", 100 - 100*len(lat)/(number_of_packets) )

print("**********************")
