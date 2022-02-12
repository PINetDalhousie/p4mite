# -*- coding: utf-8 -*-

"""
    DNS Client - DiG-like CLI utility.

    Mostly useful for testing. Can optionally compare results from two
    nameservers (--diff) or compare results against DiG (--dig).

    Usage: python -m dnslib.client [options|--help]

    See --help for usage.
"""

from __future__ import print_function

try:
    from subprocess import getoutput,getstatusoutput
except ImportError:
    from commands import getoutput,getstatusoutput

import binascii,code,pprint,sys

from dnslib.dns import DNSRecord,DNSHeader,DNSQuestion,DNSError,QTYPE,EDNS0
from dnslib.digparser import DigParser

from threading import Thread
import pandas as pd
import numpy as np


import argparse,sys,time

p = argparse.ArgumentParser(description="DNS Client")
p.add_argument("--server","-s",default="8.8.8.8",
            metavar="<address:port>",
            help="Server address:port (default:8.8.8.8:53) (port is optional)")
p.add_argument("--query",action='store_true',default=False,
            help="Show query (default: False)")
p.add_argument("--hex",action='store_true',default=False,
            help="Dump packet in hex (default: False)")
p.add_argument("--tcp",action='store_true',default=False,
            help="Use TCP (default: UDP)")
p.add_argument("--noretry",action='store_true',default=False,
            help="Don't retry query using TCP if truncated (default: false)")
p.add_argument("--diff",default="",
            help="Compare response from alternate nameserver (format: address:port / default: false)")
p.add_argument("--dig",action='store_true',default=False,
            help="Compare result with DiG - if ---diff also specified use alternative nameserver for DiG request (default: false)")
p.add_argument("--short",action='store_true',default=False,
            help="Short output - rdata only (default: false)")
p.add_argument("--dnssec",action='store_true',default=False,
            help="Set DNSSEC (DO/AD) flags in query (default: false)")
p.add_argument("--debug",action='store_true',default=False,
            help="Drop into CLI after request (default: false)")
p.add_argument("domain",metavar="<domain>",
            help="Query domain")
p.add_argument("qtype",metavar="<type>",default="A",nargs="?",
            help="Query type (default: A)")
p.add_argument('-R', '--rate', default=1, dest='rate', help='The transmit rate (request/sec). Defaults is 1', type=float)


            
args = p.parse_args()




#BUFFER_SIZE = args.buffer_size
transmit_rate = transmit_rate = args.rate
number_of_packets = transmit_rate*10
index = 0
counter_packets = 0
counter_corrects = 0



lat = []
def send_test():
    # Construct request
    start = time.time()
    try:
        q = DNSRecord(q=DNSQuestion(args.domain,getattr(QTYPE,args.qtype)))

        if args.dnssec:
            q.add_ar(EDNS0(flags="do",udp_len=4096))
            q.header.ad = 1

        address,_,port = args.server.partition(':')
        port = int(port or 53)

        a_pkt = q.send(address,port,tcp=args.tcp)
        a = DNSRecord.parse(a_pkt)

        if a.header.tc and args.noretry == False:
            # Truncated - retry in TCP mode
            a_pkt = q.send(address,port,tcp=True)
            a = DNSRecord.parse(a_pkt)

        if args.dig or args.diff:
            if args.diff:
                address,_,port = args.diff.partition(':')
                port = int(port or 53)

            if args.dig:
                if getstatusoutput("dig -v")[0] != 0:
                    p.error("DiG not found")
                if args.dnssec:
                    dig = getoutput("dig +qr +dnssec -p %d %s %s @%s" % (
                                    port, args.domain, args.qtype, address))
                else:
                    dig = getoutput("dig +qr +noedns +noadflag -p %d %s %s @%s" % (
                                    port, args.domain, args.qtype, address))
                dig_reply = list(iter(DigParser(dig)))
                # DiG might have retried in TCP mode so get last q/a
                q_diff = dig_reply[-2]
                a_diff = dig_reply[-1]
            else:
                q_diff = DNSRecord(header=DNSHeader(id=q.header.id),
                                   q=DNSQuestion(args.domain,
                                                 getattr(QTYPE,args.qtype)))
                q_diff = q
                diff = q_diff.send(address,port,tcp=args.tcp)
                a_diff = DNSRecord.parse(diff)
                if a_diff.header.tc and args.noretry == False:
                    diff = q_diff.send(address,port,tcp=True)
                    a_diff = DNSRecord.parse(diff)

        end = time.time()
        lat.append(1000*(end-start))

        if args.debug:
            code.interact(local=locals())

    except DNSError as e:
        p.error(e)
        

threads = []
while True:
	time.sleep(1/transmit_rate)
	# print("Progress: " + str(100*counter_packets/number_of_packets)+"%", end="\r")
	#my_dict = {'dst_ip': server_ip, 'dst_port': server_port,'X':size}
	newthread = Thread(target=send_test)
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
lat = [x for x in lat if x <= 50]    
print("avg: ", np.average(lat))
print("std: ", np.std(lat))
print("p95: ", np.percentile(lat,95))
print("p99: ", np.percentile(lat,99))
print("los: ", 100 - 100*len(lat)/(number_of_packets) )
# print("**********************")
