#!/usr/bin/python
import os
import time
import random 
import argparse
import sys
import socket
import struct
from datetime import datetime

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

serverBusy = False
counter_server_busy = 0
counter_setver_not_busy = 0
upper_threshold = 90
lower_threshold = 90
interval = 1/10
host_addr = sys.argv[1]
snic_addr = sys.argv[2]
test_mode = ""
try:
    test_mode = sys.argv[3]
except:
    pass

def printwt(msg):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')

def send_flag(server_addr, ara, sock):
    x = ''
    x = x.encode()
    sock.sendto(ara.encode(),server_addr)
    sock.sendto(x,server_addr)

def main():
    global serverBusy
    global counter_server_busy
    global counter_setver_not_busy

    server_addr = ('127.0.0.1', 12345)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 40000))
    if test_mode == "test":
        while True:
            print("test")
            send_flag(server_addr, snic_addr, sock)
            time.sleep(0.5)
            send_flag(server_addr, host_addr, sock)
            time.sleep(0.5)
    send_flag(server_addr, host_addr, sock)
    while True:
        x = ""
        try:
            f = open("report.log","r")
            x = f.readline()
        except:
            x = "nothing"
        x = x.strip()
        if x=="isBusy":
            send_flag(server_addr, snic_addr, sock)
            send_flag(server_addr, host_addr, sock)
            time.sleep(0.5)
            os.system("rm report.log")
        printwt(x)
        time.sleep(interval)
    printwt("DONE!")

if __name__ == '__main__':
    main()


