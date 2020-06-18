#!/usr/bin/env python2.7
#
# File: lb-test.py
#
# Description   : Test mininet virtual network for floodlight load balancer tests
# Date          : January 2019
# Last Modified : July 2020


### Imports ###
from mininet.net import Mininet
from mininet.link import TCLink, TCIntf
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
from mininet.node import RemoteController  # , OVSSwitch
from functools import partial
from mininet.util import custom
# from pycustom import CustomOVSSwitch, BadSwitch
import time
import sys

### Classes ###


class CustomTopo(Topo):
    """
    Class for custom topology implementing the structure found within load balanced network
    """

    def build(self, n=1):
        global NUM_SERVERS
        self._switches = dict()
        self._hosts = dict()
        self._links = dict()

        host_to_edge_link_cap = 100  # in Mbps
        edge_to_agg_link_cap = 1000  # in Mbps
        flooder_link_cap = 1000  # in Mbps

        # ups = self.addSwitch('ups', dpid="00:00:00:00:00:0%s" % (
        #     hex(NUM_SERVERS+1)[2:]), protocols="OpenFlow10")
        # print("ups name: " + "00:00:00:00:00:0%s" % (hex(NUM_SERVERS+1)[2:]))
        # self._switches['ups'] = ups
        # uph = self.addHost('uph')
        # self._hosts['uph'] = uph
        # upl = self.addLink(ups, uph)
        # self._links['ups-uph'] = upl
        # for i in range(1, NUM_SERVERS+1):
        #     print("name: " + "00:00:00:00:00:0%s" % (hex(i)[2:]))
        #     s = self.addSwitch('s%s' % str(
        #         i), dpid="00:00:00:00:00:0%s" % (hex(i)[2:]), protocols="OpenFlow10")
        #     self._switches['s%s' % str(i)] = s
        #     h = self.addHost('h%s' % str(i))
        #     self._hosts['h%s' % str(i)] = h
        #     l1 = self.addLink(s, h)
        #     self._links['s%s-h%s' % (str(i), str(i))] = l1
        #     l2 = self.addLink(s, ups)
        #     self._links['s%s-ups' % (str(i))] = l2

        ups = self.addSwitch('ups', dpid="00:00:00:00:00:%s" % (
            format(NUM_SERVERS+1, '02x')), protocols="OpenFlow10")
        print("ups name: " + "00:00:00:00:00:%s" %
              (format(NUM_SERVERS+1, '02x')))
        self._switches['ups'] = ups
        uph = self.addHost('uph')
        self._hosts['uph'] = uph
        upl = self.addLink(ups, uph, cls=TCLink, bw=flooder_link_cap)
        self._links['ups-uph'] = upl
        for i in range(1, NUM_SERVERS+1):
            print("name: " + "00:00:00:00:00:%s" % (format(i, '02x')))
            s = self.addSwitch('s%s' % str(
                i), dpid="00:00:00:00:00:%s" % (format(i, '02x')), protocols="OpenFlow10")
            self._switches['s%s' % str(i)] = s
            h = self.addHost('h%s' % str(i))
            self._hosts['h%s' % str(i)] = h
            l1 = self.addLink(s, h, cls=TCLink, bw=host_to_edge_link_cap)
            self._links['s%s-h%s' % (str(i), str(i))] = l1
            l2 = self.addLink(s, ups, cls=TCLink, bw=edge_to_agg_link_cap)
            self._links['s%s-ups' % (str(i))] = l2


### Functions ###


def run(target_server):
    """
    Start the network
    """
    global NUM_SERVERS
    print("Generating topo...")
    # net = Mininet(topo=CustomTopo(), controller=partial(RemoteController, ip='127.0.0.1', port=6653), xterms=True)
    # intf = custom( TCIntf, bw=100 )
    # net = Mininet(topo=CustomTopo(), controller=partial(
    #     RemoteController, ip='127.0.0.1', port=6653), link=TCLink, intf=intf)
    net = Mininet(topo=CustomTopo(), controller=partial(
        RemoteController, ip='127.0.0.1', port=6653), link=TCLink)
    net.start()
    time.sleep(3)
    print("Done")

    print("Dumping switch connections...")
    dumpNodeConnections(net.switches)
    print("Done")

    print("Dumping host IPs...")
    print("\n".join([("%s (%s)" % (h.name, h.IP())) for h in net.hosts]))
    print("Done")

    # print("Testing pingall...")  # generate flow rules
    # time.sleep(5)
    # net.pingAll()
    # print("Done")

    # print("[Sending commands to hosts...]")
    # # sleep before sending ping cmd to allow controller time to collect stats; only go to len-2 because last 2 are the servers
    # for i in range(len(net.hosts)-2):
    #     print("\t > Generating routes to servers...")
    #     # wait until this returns so we know the route was added; should we be using cmd below for ping as well? (works without, idk why)
    #     net.hosts[i].cmd("ping -c1 %s" % "10.0.0."+str(NUM_CLIENTS+1))
    #     net.hosts[i].cmd("ping -c1 %s" % "10.0.0."+str(NUM_CLIENTS+2))
    #     time.sleep(5)
    #     print("\t > Sending ping cmd to %s..." % net.hosts[i].name)
    #     net.hosts[i].sendCmd("ping %s" % target_server)
    #     print("\t Waiting for floodight statistics service to collect new stats for next client...\n")
    #     if i < (len(net.hosts)-2-1):
    #         time.sleep(15)
    # print("[Done]\n")
    # print(vars(net))
    # print(vars(net.switches[0].defaultIntf()))
    # print("[Sending discovery (ping) packets out hosts toward agg switch (ups)...]")
    # print("[Starting ping scripts on nodes...")
    # sleep before sending ping cmd to allow controller time to collect stats; only go to len-2 because last 2 are the servers
    # for i in range(0, NUM_SERVERS):  # dont start on uph
        # print("> Pinging from h%s..." % (str(i)))
        # wait until this returns so we know the route was added; should we be using cmd below for ping as well? (works without, idk why)
        # print(net.hosts[i].cmd("ping -c1 127.0.0.1"))
        # time.sleep(5)

    # print("\t Waiting for floodight statistics service to collect new stats for next client...\n")
    # if i < (len(net.hosts)-2-1):
    #     time.sleep(15)
    print("[Done]\n")

    print("Starting CLI...")
    net.interact()
    print("Done")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Missing argument for target server or number of clients.")
        print("\nUsage: <num_clients> <target_server>\n")
    else:
        NUM_SERVERS = int(sys.argv[1])
        run(sys.argv[2])
