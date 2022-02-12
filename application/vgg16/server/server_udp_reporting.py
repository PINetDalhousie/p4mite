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
from PIL import Image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential

model_ = tf.keras.models.load_model('models/vgg.h5')


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


class UDPServerMultiClient(udp_server.UDPServer):
	''' A simple UDP Server for handling multiple clients '''

	def __init__(self, host, port):
		super().__init__(host, port)
		self.socket_lock = threading.Lock()
	def handle_request(self, data, client_address, recived_f):
		''' Handle the client '''
		global average_lat
		# handle request
		client_address = ("10.50.0.1",client_address[1])
		start = time.time()
		self.printwt(f'[ REQUEST from {client_address} ]')
		img = Image.open(recived_f).convert("RGB")
		img = img.resize((180, 180))
		input_data = np.array(img, dtype=np.float32)
		input_data = np.expand_dims(input_data, axis=0)
		img.close()
		p = model_(input_data)
		p = p[0][0]
		p = 1 if p>0.5 else 0
		response = str(6)
		self.printwt(f'[ RESPONSE is {response} ]')		# send response to the client
		self.printwt(f'[ RESPONSE to {client_address} ]')
		with self.socket_lock:
			self.sock.sendto(response.encode(), client_address)

		os.remove(recived_f)
		end = time.time()
		average_lat = 0.2*average_lat + 0.8*1000*(end-start)
		self.printwt("lat: "+str(average_lat))
		if average_lat > 150:
			os.system("echo isBusy > report.log")
	def wait_for_client(self):
		''' Wait for clients and handle their requests '''
		global BUFFER_SIZE
		try:
			while True: # keep alive
				try: # receive request from client
					data, client_address = self.sock.recvfrom(BUFFER_SIZE)
					recived_f = './tmp/' + str(uuid.uuid4()) + '.jpg'
					f = open(recived_f, 'wb')
					while True:
						f.write(data)
						data, client_address = self.sock.recvfrom(BUFFER_SIZE)
						if data==b'':
							f.close()
							break
					self.printwt("File has been downloaded!")
					c_thread = threading.Thread(target = self.handle_request,
					                        args = (data, client_address,recived_f))
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


