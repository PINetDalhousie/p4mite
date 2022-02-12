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
import idx2numpy
from sklearn.neighbors import KNeighborsClassifier


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

args = parser.parse_args()


server_ip = args.host
server_port = args.port
BUFFER_SIZE = args.BS
# print("The host is " + server_ip)
# print("The port is " + str(server_port))
# print("The buffer size is " + str(BUFFER_SIZE))
average_lat = 0
train_x_path = "mnist/train-images-idx3-ubyte"
train_y_path = "mnist/train-labels-idx1-ubyte"

test_x_path = "mnist/t10k-images-idx3-ubyte"
test_y_path = "mnist/t10k-labels-idx1-ubyte"

train_x = []
train_y = []

train_x = idx2numpy.convert_from_file(train_x_path)
train_y = idx2numpy.convert_from_file(train_y_path)
train_x = np.reshape(train_x, (60000, 28*28))
neigh = KNeighborsClassifier(n_neighbors=3)
neigh.fit(train_x, train_y)


class UDPServerMultiClient(udp_server.UDPServer):
	''' A simple UDP Server for handling multiple clients '''

	def __init__(self, host, port):
		super().__init__(host, port)
		self.socket_lock = threading.Lock()
	def handle_request(self, data, client_address):
		''' Handle the client '''
		# handle request
		client_address = ("10.50.0.1",client_address[1])
		global average_lat
		start = time.time()
		self.printwt('[ REQUEST from ' + str(client_address) + ' ]')
		input_data = data.decode()
		input_data = input_data[1:-1].split()
		input_array = np.array([int(i) for i in input_data])
		input_array = input_array.reshape(1,len(input_data))
		p = neigh.predict(input_array)
		p = p[0]
		resp = str(6)
		self.printwt("RESPONSE is " + str(resp))		# send response to the client
		self.printwt('[ RESPONSE to ' + str(client_address) + ' ]')
		with self.socket_lock:
			self.sock.sendto(resp.encode(), client_address)
		end = time.time()
		average_lat = 0.2*average_lat + 0.8*1000*(end-start)
		self.printwt("lat: " + str(average_lat))
		if average_lat > 300:
			os.system("echo isBusy > report.log")
	def wait_for_client(self):
		''' Wait for clients and handle their requests '''
		global BUFFER_SIZE
		try:
			while True: # keep alive
				try: # receive request from client
					data, client_address = self.sock.recvfrom(BUFFER_SIZE)
					self.printwt("New connection!")
					while True:
						x, client_address = self.sock.recvfrom(BUFFER_SIZE)
						data += x
						if x==b'':
							break
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


