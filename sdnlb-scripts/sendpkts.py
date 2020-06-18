#!/usr/bin/env python3.7
#
# File: sendpkts.py
#
# Description   : flooder script
# Date          : November 2019
# Last Modified : July 2020


### Imports ###
import random
from scapy.all import *
import time
import threading
import sys
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
import socket
import struct


### Classes ###
class Flow():
    def __init__(self, bytes_left=0, rate=0, duration=0, src_ip=None):
        self.bytes_left = bytes_left
        self.rate = rate
        self.duration = duration
        self.src_ip = src_ip


### Functions ###
def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def generate_flows(_sim_time, _client_rate):
    num_flows = _sim_time * _client_rate

    # See https://docs.scipy.org/doc/numpy-1.15.0/reference/generated/numpy.random.pareto.html for generating random.samples with numpy pareto; specifically, using the formula below to obtain classical pareto from the pareto2/lomax dist

    # generate sizes
    # xm1 = 10.0  # scale
    xm1 = 600.0  # scale
    # a1 = 1.2  # shape
    a1 = 1.1  # shape
    sizes = sorted((np.random.pareto(a1, num_flows) + 1) * xm1)

    # generate durations
    xm2 = 0.001
    a2 = 1.5
    durs = sorted((np.random.pareto(a2, num_flows) + 1) * xm2)

    # sort/match to create flows
    flows = dict()
    used_ips = set()  # wow... about 100x faster when checking membership
    print("num_flows: ", num_flows)
    # 167772172 is 10.0.0.12; edit 1/15: this might be bad for pool 25; meh prob not really tho
    for i in range(167772172, 167772172+num_flows):
        src_ip = int2ip(i)
        if len(flows.keys()) % int(0.01*num_flows) == 0:
            print("\rGenerating flows [%d%%]" % int(
                len(flows.keys())/num_flows*100), end='')

        # deal with very large flows that don't fit in MTU; need to extend duration
        idx = i - 167772172
        if sizes[idx]/durs[idx] > 1472:
            # just update to set below rate to 1472
            durs[idx] = np.ceil(sizes[idx]/1472)
        flows[src_ip] = Flow(sizes[idx], sizes[idx] /
                             durs[idx], durs[idx], src_ip)

    # gr = plt.GridSpec(1, 7, wspace=0.4, hspace=0.3)
    # cdf_sz = calc_cdf_fast(sizes)
    # plt.subplot(gr[:, :3])
    # plt.xlabel('Flow size (B)')
    # plt.ylabel('Cumulative Probability')
    # plt.title('Flow Sizes')
    # plt.plot(sizes, cdf_sz, color='green')
    # cdf_durs = calc_cdf_fast(durs)
    # plt.subplot(gr[:, 4:])
    # plt.xlabel('Durations (s)')
    # plt.ylabel('Cumulative Probability')
    # plt.title('Flow Durations')
    # plt.plot(durs, cdf_durs, color='red')
    # plt.show()
    print("\rGenerating flows [100%%]")
    return flows


def calc_cdf_fast(arr):
    cdf = []
    for val in arr:
        count = 0
        for other_val in arr:
            if other_val <= val:
                count += 1
        cdf.append(float(count*1.0/len(arr)))
    return cdf


def make_pkt(_flow, _num_bytes):
    return IP(src=_flow.src_ip, dst="10.0.0.100", proto=0x01)/ICMP(type=8)/Raw(load='0'*int(_num_bytes))


def generate_packets(_sim_time, _client_rate, _flows, _collection_interval):
    # Note: control traffic doesnt have to be simulated as it already exists naturally in the virtual network
    # Note: send the flows toward the edge switch (ups) connecting to the servers (h1-h10) do we want to update the flows then send, or do we want to update the flows and send at the same time above? We want to send with respect to each source so aggregating them here with total_send_bytes may not be the correct way;

    recent_flows = dict()
    next_batch = list()
    keys = list(_flows.keys())
    random.shuffle(keys)  # shuffle before beginning simulation
    client_counter = 0
    for i in range(sim_time):
        for j in range(_client_rate):
            recent_flows[keys[client_counter]] = _flows[keys[client_counter]]
            client_counter += 1

        # update existing flows
        tmp_keys = list(recent_flows.keys())
        for key in tmp_keys:
            if recent_flows[key].duration == 0:
                # just remove (removed first in the simulator but we do it here)
                del recent_flows[key]  # clean keys
            elif recent_flows[key].duration <= 1.0:
                next_batch.append(
                    make_pkt(recent_flows[key], recent_flows[key].bytes_left))
                recent_flows[key].bytes_left = 0
                recent_flows[key].duration = 0
            elif recent_flows[key].duration > 1.0:
                if recent_flows[key].bytes_left == 0:
                    del recent_flows[key]
                elif recent_flows[key].bytes_left <= recent_flows[key].rate:
                    next_batch.append(
                        make_pkt(recent_flows[key], recent_flows[key].bytes_left))
                    recent_flows[key].bytes_left = 0
                    recent_flows[key].duration = 0
                elif recent_flows[key].bytes_left > recent_flows[key].rate:
                    next_batch.append(
                        make_pkt(recent_flows[key], recent_flows[key].rate))
                    recent_flows[key].bytes_left -= recent_flows[key].rate
                    recent_flows[key].duration -= 1.0
                else:
                    del recent_flows[key]
            else:
                del recent_flows[key]

        if i % int(0.01*sim_time) == 0:
            print("\rGenerating packets from flows [%d%%]" % int(
                i*1.0/sim_time*100), end='')

    print("\rGenerating packets from flows [100%%]")
    print("Avg pkt size: %.2f bytes" %
          (np.mean([len(pkt) for pkt in next_batch])))
    print("Saving pcap")
    wrpcap('flooder-600xm-1.1a.pcap.gz', next_batch, gz=1, append=True)


def send_flow_bytes(_next_batch, inter=0.0005):
    send(_next_batch, count=1, inter=inter, iface="uph-eth0", verbose=None)


def flood(_next_batch):
    print("\n[Got packets. Running flooder...]")
    send_flow_bytes(_next_batch, 0.0005)


if __name__ == '__main__':
    # for i in range(1):  # slow test
    #     for i in range(35, 45):
    #         # pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
    #         #     random.randint(0, 255)), str(random.randint(12, 99))), dst="10.0.0.100") / \
    #         #     ICMP()/Raw(load='0'*1000)
    #         pkt = IP(src='10.0.0.%d' % i, dst="10.0.0.100") / \
    #             ICMP()/Raw(load='0'*1472)
    #         # pkt = IP(src='10.0.0.%d' % i, dst="10.0.0.100") / \
    #         #     TCP()/Raw(load='0'*1460)
    #         print(pkt.summary(), "(len: ", len(pkt), ")")
    #         # send(pkt, count=10, inter=0.1, iface="uph-eth0")
    #         # send([pkt, pkt], count=1, iface="uph-eth0", verbose=None)
    #         send(pkt, count=1, iface="uph-eth0", verbose=None)
    #         time.sleep(1)
    #     # print("waiting")
    #     # time.sleep(10)
    # exit(1)

    # flood_start = time.time()
    # for i in range(10000):  # fast test (max pkt size); also changed to only send the pkt once
    #     # pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
    #     #     random.randint(0, 255)), str(random.randint(12, 99))), dst="10.0.0.100") / \
    #     #     TCP(sport=6000, dport=6000)/Raw(load='0'*1460)
    #     pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
    #         random.randint(0, 255)), str(random.randint(12, 99))), dst="10.0.0.100", proto=0x01) / \
    #         ICMP(type=8)/Raw(load='0'*1400) # 42 extra bytes when using ethernet frame?; saw this 42 before in PACKET_IN...
    #     print(pkt.summary(), "(len: ", len(pkt), ")")
    #     # send(pkt, count=10, inter=0.1, iface="uph-eth0")
    #     send(pkt, count=1, iface="uph-eth0", verbose=None) # only need count 1 so we can get diff IP
    #     print("Time since last pkt: ", time.time()-flood_start)
    #     flood_start = time.time()
    #     # time.sleep(0.25)
    # exit(1)

    # start = time.time_ns()
    # f = [0]*1800000
    # for i in range(1800000):
    #     f[i] = i
    # print("elapsed: ", str((time.time_ns()-start)/1e9), "s")
    # print("len: ", str(len(f)))
    # # print("f: ", f)
    # exit(0)

    # Note: only one server known to flooders "10.0.0.100"
    sim_time = 900  # in seconds
    client_rate = 1000  # new incoming flows per second
    collection_interval = 1.0

    if (sys.argv[1] == 'o'):  # open packets from pcap
        pkts = rdpcap('flooder-500-1800.pcap')
        flood(pkts)
    elif (sys.argv[1] == 'p'):
        # generate new packets (using distribution instead of fixed size like below)
        flows = generate_flows(sim_time, client_rate)
        # exit(1)
        # print("\n[Flows generated. Running flooder...]")
        # num_flooders = 1
        # nf = len(flows)/num_flooders  # evenly divide flows for each flooder
        # flooders = [None]*num_flooders
        # for i in range(num_flooders):
        #     flooders[i] = threading.Thread(
        #         target=flood, args=(flows[int(i*nf):int((i+1)*nf)], i))
        #     flooders[i].start()

        # # wait for flooders to finish
        # for i in range(num_flooders):
        #     flooders[i].join()
        generate_packets(sim_time, client_rate, flows, collection_interval)
    elif (sys.argv[1] == 'f2'):
        # build arr of sizes (durs are just 1 pkt basically) and multiply that by '0' so we dont have to load pcap every time
        flood_start = time.time()

        # generate sizes
        xm1 = 10.0  # scale
        a1 = 1.2  # shape
        # sizes = sorted((np.random.pareto(a1, num_flows) + 1) * xm1)
        sizes = (np.random.pareto(a1, int(sim_time*client_rate)) +
                 1) * xm1  # dont sort

        num_flows = int(1e3)
        pkts = [None]*num_flows
        for i in range(num_flows):
            if sizes[i] > 1470:
                sizes[i] = 1470
            pkts[i] = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
                random.randint(0, 255)), str(random.randint(30, 99))), dst="10.0.0.100", proto=0x01) / \
                ICMP(type=8)/Raw(load='0' *
                                 1472)  # was going from .12 before, not sure how that affected pool 25; likely doesnt matter
            # pkts[i] = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
            #     random.randint(0, 255)), str(random.randint(30, 99))), dst="10.0.0.100", proto=0x01) / \
            #     ICMP(type=8)/Raw(load='0'*int(sizes[i])) # was going from .12 before, not sure how that affected pool 25; likely doesnt matter
            # print(pkts[i].summary(), "(len: ", len(pkts[i]), ")")
            if (i % (0.01*num_flows)) == 0:
                print("\rGen flows [%d%%]" % (i/num_flows*100), end='')
        print("\rGen flows [100%%]")

        n = int((sim_time*client_rate)/num_flows)  # recycle n times
        for i in range(n):
            # send(pkts, count=1, inter=0.000575, iface="uph-eth0", verbose=None)
            # send(pkts, count=1, inter=0.0005, iface="uph-eth0", verbose=None)
            send(pkts, count=1, inter=0.001, iface="uph-eth0", verbose=None)
            # if i==0:
            #     print("Sleeping to let rules install...")
            #     time.sleep(20)
            #     print("Done sleeping.")
        # s = conf.L3socket(iface='uph-eth0')
        # for i in range(n):
        #     for j in range(len(pkts)):
        #         s.send(pkts[j])

        # for i in range(int(1e9)):  # fast test (max pkt size); also changed to only send the pkt once
        #     # pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
        #     #     random.randint(0, 255)), str(random.randint(12, 99))), dst="10.0.0.100") / \
        #     #     TCP(sport=6000, dport=6000)/Raw(load='0'*1460)
        #     pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
        #         random.randint(0, 255)), str(random.randint(12, 99))), dst="10.0.0.100", proto=0x01) / \
        #         ICMP(type=8)/Raw(load='0'*int(sizes[i])) # 42 extra bytes when using ethernet frame?; saw this 42 before in PACKET_IN...
        #     print(pkt.summary(), "(len: ", len(pkt), ")")
        #     # send(pkt, count=10, inter=0.1, iface="uph-eth0")
        #     send(pkt, count=1, iface="uph-eth0", verbose=None) # only need count 1 so we can get diff IP
        #     # print("Time since last pkt: ", time.time()-flood_start)
        #     flood_start = time.time()
        #     # time.sleep(0.25)
        exit(1)
    elif (sys.argv[1] == 'm'):  # generate max size pkts (for long flows)
        num_pkts = int(1e6)
        pkts = []
        for i in range(num_pkts):
            pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
                random.randint(0, 255)), str(random.randint(30, 99))), dst="10.0.0.100", proto=0x01)/ICMP(type=8)/Raw(load='0'*int(1472))
            # print("len of pkt: %d" % len(pkt))
            if len(pkts) % int(0.01*num_pkts) == 0:
                print("\rGenerating pkts [%d%%]" %
                      int(len(pkts)/num_pkts*100), end='')
            pkts.append(pkt)
        print("\rGenerating flows [100%%]")
        print("Saving pcap")
        wrpcap('flooder-long-%.2fM-flows.pcap.gz' %
               (num_pkts*1.0/1e6), pkts, gz=1, append=True)
    elif (sys.argv[1] == 's'):  # single pkt
        pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(random.randint(0, 255)), str(
            random.randint(30, 99))), dst="10.0.0.100", proto=0x01)/ICMP(type=8)/Raw(load='0'*1472)
        # num_pkts = int(1e6)
        # pkts = [pkt]*num_pkts
        # n = 100
        # for i in range(n):
        #     send(pkts, iface="uph-eth0", verbose=None)
        wrpcap('single-pkt.pcap.gz', pkt, gz=1, append=True)
    elif (sys.argv[1] == 'sm'):  # generate large pkts (for short flows)
        num_pkts = int(1e6)
        pkts = []
        for i in range(num_pkts):
            # pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
            #     random.randint(0, 255)), str(random.randint(30, 99))), dst="10.0.0.100", proto=0x01)/ICMP(type=8)/Raw(load='0'*int(600))
            pkt = IP(src="10.%s.%s.%s" % (str(random.randint(0, 255)), str(
                random.randint(0, 255)), str(random.randint(30, 99))), dst="10.0.0.100", proto=0x01)/ICMP(type=8)/Raw(load='0'*int(1072))
            # print("len of pkt: %d" % len(pkt))
            if len(pkts) % int(0.01*num_pkts) == 0:
                print("\rGenerating pkts [%d%%]" %
                      int(len(pkts)/num_pkts*100), end='')
            pkts.append(pkt)
        print("\rGenerating flows [100%%]")
        print("Saving pcap")
        wrpcap('flooder-short-%.2fM-flows.pcap.gz' %
               (num_pkts*1.0/1e6), pkts, gz=1, append=True)
