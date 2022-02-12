import sys
import re
import time
import os
import random
import argparse
import socket
import struct

from datetime import datetime
from threading import Thread, Timer
from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP

serverBusy = False
counter_server_busy = 0
counter_setver_not_busy = 0
interval = 1/10
host_addr = sys.argv[1]
snic_addr = sys.argv[2]
threshold = int(sys.argv[3])

test_mode = ""
try:
    test_mode = sys.argv[4]
except:
    pass
interface = "enp101s0f0"

IP_REGEX = re.compile('[0-9\.]+\s>\s[0-9\.]+')


def printwt(msg):
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')






connection_list = {}
average_lat = 0
port_list = [i for i in range(10001,10021)]
port_list.append(12345)

# print(port_list)

def time_diff(end, start):
    end = [float(x) for x in end.split(":")]
    start = [float(x) for x in start.split(":")]
    if end[0] == start[0] and end[1] == start[1]:
        return 1000*(end[2] - start[2])
    elif end[0] == start[0]:
        end[2] +=60
        return 1000*(end[2] - start[2])



def process(data):
    global average_lat
    ip_string = IP_REGEX.findall(data[:-1])
    log = ip_string[0] if ip_string else ''
    sys.stdout.flush()
    log = log.split()
    src = log[0].split(".")
    dst = log[-1].split(".")
    time = data.split()[0]
    if int(dst[-1]) in port_list and not(src[-1] in connection_list):
        start = data.split()[0]
        connection_list[src[-1]] = start
    elif int(src[-1]) in port_list and dst[-1] in connection_list:
        end = data.split()[0]
        start = connection_list.pop(dst[-1])
        average_lat = time_diff(end,start)


def looper():    
    # i as interval in seconds
    global connection_list
    global average_lat
    average_lat = 0
    print("looper", average_lat)
    connection_list = {}
    Timer(10, looper).start()    
looper()


def send_server_is_busy():
    printwt("Request to say server is BUSY!")
    global average_lat
    global connection_list
    #connection_list = {}
    # average_lat = 0
    iface = interface
    s_port = 9876
    d_port = 9876
    src_addr = snic_addr
    dst_addr = "10.50.0.101"
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=dst_addr,src=src_addr) / UDP(dport=d_port, sport=s_port)
    sendp(pkt, iface=iface, verbose=False)
    src_addr = host_addr
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=dst_addr,src=src_addr) / UDP(dport=d_port, sport=s_port)
    #pkt.show2()
    sendp(pkt, iface=iface, verbose=False)
    time.sleep(0.4)



data = ''
send_server_is_busy()
while 1:
    try:
        data += sys.stdin.read(1)
        if data.endswith('\n'):
            # print(data)
            t = Thread(target = process, args =(data, ), daemon = True)
            t.start()
            t.join()
            # print(average_lat)
            if average_lat>threshold:
                #send_server_is_busy()
                t2 = Thread(target = send_server_is_busy, args =(), daemon = True)
                t2.start()
                t2.join()
            data = ''
    except KeyboardInterrupt:
        sys.stdout.flush()
        break





