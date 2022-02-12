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

from udp_raw import *
from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP


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
SP = [i for i in range(10001,10021)]
#SP = [12345]
class UDPServerMultiClient(udp_server.UDPServer):
	''' A simple UDP Server for handling multiple clients '''

	def __init__(self, host, port):
		super().__init__(host, port)
		self.socket_lock = threading.Lock()
		self.ara = "10.50.0.6"
		self.printwt("ARA: " + self.ara)
		self.connection = {}
		self.counter = 0
	def handle_request(self, data, client_address):
		''' Handle the client '''

		# handle request
		if client_address[1] == 9876:
			self.ara = data.decode()
			self.printwt("ARA: " + str(self.ara))
		else:
			print("load balancing!")
			dst_address = (self.ara,SP[self.counter])
			self.counter+=1
			if self.counter >= len(SP): self.counter=0
			print(dst_address)
			print(client_address)
			chunks = [data[i:i+BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)]
			for chunk in chunks:
				udp_send(chunk, dst_address, client_address)
			e = ''
			udp_send(e.encode(), dst_address, client_address)

	def wait_for_client(self):
		''' Wait for clients and handle their requests '''
		global BUFFER_SIZE
		try:
			while True: # keep alive
				try: # receive request from client
					data, client_address = self.sock.recvfrom(BUFFER_SIZE)
					if client_address[0]+':'+str(client_address[1]) in self.connection:
						self.connection[client_address[0]+':'+str(client_address[1])] += data
					else:
						self.connection[client_address[0]+':'+str(client_address[1])] = data

					if data ==b'':
						data = self.connection.pop(client_address[0]+':'+str(client_address[1]))
						#data.decode()
						self.printwt(f'[ REQUEST ends {client_address} ]')
						c_thread = threading.Thread(target = self.handle_request,
													args = (data, client_address))
						c_thread.daemon = True
						c_thread.start()

					# while True:
					# 	d, client_address = self.sock.recvfrom(BUFFER_SIZE)
					# 	data+=d
					# 	if d==b'':
					# 		break
					# data.decode()
					# self.printwt(f'[ REQUEST ends {client_address} ]')
					# c_thread = threading.Thread(target = self.handle_request,
					# 							args = (data, client_address))
					# c_thread.daemon = True
					# c_thread.start()


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


