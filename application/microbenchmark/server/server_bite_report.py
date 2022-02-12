import socket
import threading
import udp_server
from datetime import datetime
import argparse
import uuid
import random
import time
import os
import numpy as np

from multiprocessing import Process


parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host',
					default='127.0.0.1',
					dest='host',
					help='Pass the IP of Host. Defaults is localhost',
					type=str
					)

parser.add_argument('-P', '--port',
					default=12345,
					dest='port',
					help='Provide the Host port number. Defaults to 12345',
					type=int
					)
parser.add_argument('-B', '--buffer',
					default=1024,
					dest='BS',
					help='The buffer size. Defaults to 1024',
					type=int
					)


parser.add_argument('-T', '-threshold',
                                        default=300,
                                        dest='th',
                                        help='The threhold',
                                        type=int
                                        )


args = parser.parse_args()


server_ip = args.host
server_port = args.port
BUFFER_SIZE = args.BS
average_lat = 0
isBusy = 0
threshold = args.th
# print("The host is " + server_ip)
# print("The port is " + str(server_port))
# print("The buffer size is " + str(BUFFER_SIZE))


def micro(size):
	for i in range(size):
		for j in range(1,160):
			for k in range(1,1000):
				a = i*j//k

class UDPServerMultiClient(udp_server.UDPServer):
	''' A simple UDP Server for handling multiple clients '''

	def __init__(self, host, port):
		super().__init__(host, port)
		self.socket_lock = threading.Lock()



	def benchmark(self, size):

		processes = []
		for i in range(1): processes.append(Process(target=micro, args=(size,)))
		for process in processes: process.start()
		for process in processes: process.join()
		return 6


	def handle_request(self, data, client_address):
		''' Handle the client '''
		# handle request
		client_address = ("10.50.0.1", client_address[1])
		start = time.time()
		size = int(data.decode())
		#resp = str(self. benchmark(size))
		resp = str(6)
		self.printwt("RESPONSE is " + str(resp))		# send response to the client
		with self.socket_lock:
			self.sock.sendto(resp.encode(), client_address)
		end = time.time()

		if 1000*(end-start) > threshold:
			os.system("echo isBusy > ../report.log")
	def wait_for_client(self):
		''' Wait for clients and handle their requests '''
		global BUFFER_SIZE
		try:
			while True: # keep alive
				try: # receive request from client
					data, client_address = self.sock.recvfrom(BUFFER_SIZE)
					self.sock.recvfrom(BUFFER_SIZE)
					recived_f = './tmp/' + str(uuid.uuid4())
					#while True:
					#	x, client_address = self.sock.recvfrom(BUFFER_SIZE)
					#	data += x
					#	if x==b'':
					#		break
					self.printwt("Request has been received!")
					c_thread = threading.Thread(target = self.handle_request,
					                        args = (data, client_address))
					c_thread.daemon = True
					c_thread.start()

				except OSError as err:
					self.printwt(err)
					break

		except KeyboardInterrupt:
			self.shutdown_server()

def main():
	global server_ip, server_port, BUFFER_SIZE
	udp_server_multi_client = UDPServerMultiClient(server_ip, server_port)
	udp_server_multi_client.configure_server()
	udp_server_multi_client.wait_for_client()

if __name__ == '__main__':
	main()



