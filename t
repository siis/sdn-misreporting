2019-12-08 20:09:18.602 INFO  [n.f.c.m.FloodlightModuleLoader] Loading modules from src/main/resources/floodlightdefault.properties
2019-12-08 20:09:18.776 WARN  [n.f.r.RestApiServer] HTTPS disabled; HTTPS will not be used to connect to the REST API.
2019-12-08 20:09:18.776 WARN  [n.f.r.RestApiServer] HTTP enabled; Allowing unsecure access to REST API on port 8080.
2019-12-08 20:09:18.776 WARN  [n.f.r.RestApiServer] CORS access control allow ALL origins: true
2019-12-08 20:09:18.965 WARN  [n.f.c.i.OFSwitchManager] SSL disabled. Using unsecure connections between Floodlight and switches.
2019-12-08 20:09:18.966 INFO  [n.f.c.i.OFSwitchManager] Clear switch flow tables on initial handshake as master: TRUE
2019-12-08 20:09:18.966 INFO  [n.f.c.i.OFSwitchManager] Clear switch flow tables on each transition to master: TRUE
2019-12-08 20:09:18.966 INFO  [n.f.c.i.OFSwitchManager] Setup default rules for all tables on switch connect: true
2019-12-08 20:09:18.974 INFO  [n.f.c.i.OFSwitchManager] Setting 0x1 as the default max tables to receive table-miss flow
2019-12-08 20:09:19.28 INFO  [n.f.c.i.OFSwitchManager] OpenFlow version OF_15 will be advertised to switches. Supported fallback versions [OF_10, OF_11, OF_12, OF_13, OF_14, OF_15]
2019-12-08 20:09:19.30 INFO  [n.f.c.i.OFSwitchManager] Listening for OpenFlow switches on [0.0.0.0]:6653
2019-12-08 20:09:19.30 INFO  [n.f.c.i.OFSwitchManager] OpenFlow socket config: 1 boss thread(s), 16 worker thread(s), 60000 ms TCP connection timeout, max 1000 connection backlog, 4194304 byte TCP send buffer size
2019-12-08 20:09:19.31 INFO  [n.f.c.i.Controller] ControllerId set to 1
2019-12-08 20:09:19.31 INFO  [n.f.c.i.Controller] Shutdown when controller transitions to STANDBY HA role: true
2019-12-08 20:09:19.31 WARN  [n.f.c.i.Controller] Controller will automatically deserialize all Ethernet packet-in messages. Set 'deserializeEthPacketIns' to 'FALSE' if this feature is not required or when benchmarking core performance
2019-12-08 20:09:19.32 INFO  [n.f.c.i.Controller] Controller role set to ACTIVE
2019-12-08 20:09:19.84 INFO  [n.f.l.i.LinkDiscoveryManager] Link latency history set to 10 LLDP data points
2019-12-08 20:09:19.86 INFO  [n.f.l.i.LinkDiscoveryManager] Latency update threshold set to +/-0.5 (50.0%) of rolling historical average
2019-12-08 20:09:19.88 INFO  [n.f.t.TopologyManager] Path metrics set to LATENCY
2019-12-08 20:09:19.88 INFO  [n.f.t.TopologyManager] Will compute a max of 3 paths upon topology updates
2019-12-08 20:09:19.103 INFO  [n.f.f.Forwarding] Default hard timeout not configured. Using 0.
2019-12-08 20:09:19.103 INFO  [n.f.f.Forwarding] Default idle timeout set to 5.
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Default table ID not configured. Using 0x0.
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Default priority not configured. Using 1.
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Default flags will be set to SEND_FLOW_REM false.
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Default flow matches set to: IN_PORT=true, VLAN=true, MAC=true, IP=true, FLAG=true, TPPT=true
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Default detailed flow matches set to: SRC_MAC=true, DST_MAC=true, SRC_IP=true, DST_IP=true, SRC_TPPT=true, DST_TPPT=true
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Not flooding ARP packets. ARP flows will be inserted for known destinations
2019-12-08 20:09:19.104 INFO  [n.f.f.Forwarding] Flows will be removed on link/port down events
2019-12-08 20:09:19.104 INFO  [n.f.s.StatisticsCollector] Statistics collection disabled
2019-12-08 20:09:19.104 INFO  [n.f.s.StatisticsCollector] Port statistics collection interval set to 10s
2019-12-08 20:09:19.106 INFO  [n.f.h.HAController] Configuration parameters: {serverPort=127.0.0.1:4242, nodeid=1} 1 
2019-12-08 20:09:19.137 INFO  [o.s.s.i.SyncManager] [1] Updating sync configuration ClusterConfig [allNodes={1=Node [hostname=192.168.56.1, port=6642, nodeId=1, domainId=1], 2=Node [hostname=192.168.56.1, port=6643, nodeId=2, domainId=1], 3=Node [hostname=192.168.56.1, port=6644, nodeId=3, domainId=1], 4=Node [hostname=192.168.56.1, port=6645, nodeId=4, domainId=1]}, authScheme=CHALLENGE_RESPONSE, keyStorePath=/etc/floodlight/myKey.jceks, keyStorePassword is set]
2019-12-08 20:09:19.253 INFO  [o.s.s.i.r.RPCService] Listening for internal floodlight RPC on 0.0.0.0/0.0.0.0:6642
2019-12-08 20:09:19.291 INFO  [n.f.h.HAController] LDHAWorker is starting...
2019-12-08 20:09:19.293 INFO  [n.f.h.HAController] TopoHAWorker is starting...
2019-12-08 20:09:19.325 INFO  [n.f.h.AsyncElection] [AsyncElection] Priorities are not set.
2019-12-08 20:09:19.327 INFO  [n.f.h.HAController] HAController is starting...
2019-12-08 20:09:19.356 INFO  [n.f.h.ControllerLogic] [ControllerLogic] Running...
2019-12-08 20:09:19.380 INFO  [n.f.h.HAServer] Starting HAServer...
2019-12-08 20:09:19.451 INFO  [o.r.C.I.Server] Starting the Simple [HTTP/1.1] server on port 8080
2019-12-08 20:09:19.451 INFO  [org.restlet] Starting net.floodlightcontroller.restserver.RestApiServer$RestApplication application
2019-12-08 20:09:21.731 INFO  [n.f.j.JythonServer] Starting DebugServer on :6655
2019-12-08 20:09:31.588 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:41702
2019-12-08 20:09:31.611 INFO  [n.f.c.i.OFChannelHandler] [[? from 127.0.0.1:41702]] Disconnected connection
2019-12-08 20:09:33.173 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:46934
2019-12-08 20:09:33.213 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47028
2019-12-08 20:09:33.268 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47114
2019-12-08 20:09:33.305 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47170
2019-12-08 20:09:33.351 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47238
2019-12-08 20:09:33.389 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47384
2019-12-08 20:09:33.424 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47542
2019-12-08 20:09:33.452 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47660
2019-12-08 20:09:33.477 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47768
2019-12-08 20:09:33.501 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47878
2019-12-08 20:09:33.526 INFO  [n.f.c.i.OFChannelHandler] New switch connection from /127.0.0.1:47988
2019-12-08 20:09:33.555 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:46934 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47238 using lesser hello header algorithm.
2019-12-08 20:09:33.555 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47768 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47114 using lesser hello header algorithm.
2019-12-08 20:09:33.555 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47170 using lesser hello header algorithm.
2019-12-08 20:09:33.555 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47660 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47542 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47988 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47028 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47878 using lesser hello header algorithm.
2019-12-08 20:09:33.556 INFO  [n.f.c.i.OFChannelHandler] Negotiated down to switch OpenFlow version of OF_10 for /127.0.0.1:47384 using lesser hello header algorithm.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47542 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47768 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47238 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:46934 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47114 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47028 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47170 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47988 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47660 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.577 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47384 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.584 WARN  [n.f.c.i.OFChannelHandler] Ignoring PORT_STATUS message from /127.0.0.1:47878 during OpenFlow channel establishment. Ports will be explicitly queried in a later state.
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:06] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:02] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:01] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:03] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:0a] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:05] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:04] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:08] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:09] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.665 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:07] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.666 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Switch OFSwitch DPID[00:00:00:00:00:00:00:0b] bound to class class net.floodlightcontroller.core.internal.OFSwitch, description SwitchDescription [manufacturerDescription=Nicira, Inc., hardwareDescription=Open vSwitch, softwareDescription=2.12.90, serialNumber=None, datapathDescription=None]
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.667 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Defining switch role from config file: ROLE_MASTER
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:07 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:03 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:05 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:06 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:02 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:01 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:0a on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:04 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:0b on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:08 on upcoming transition to MASTER.
2019-12-08 20:09:33.675 INFO  [n.f.c.i.OFSwitchHandshakeHandler] Clearing flow tables of 00:00:00:00:00:00:00:09 on upcoming transition to MASTER.
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
operations: 
Switch Updated
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
operations: 
Link Updated
2019-12-08 20:09:33.772 INFO  [n.f.t.TopologyManager] Recomputing topology due to: link-discovery-updates
operations: 
Port Up
Port Up
operations: 
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
2019-12-08 20:09:33.837 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:0b, port=8, activeSince=Sun Dec 08 20:09:33 EST 2019, lastSeen=Sun Dec 08 20:09:33 EST 2019]]  newmap null 
2019-12-08 20:09:33.837 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:05, port=2, activeSince=Sun Dec 08 20:09:33 EST 2019, lastSeen=Sun Dec 08 20:09:33 EST 2019]]  newmap null 
operations: 
Port Up
Port Up
Port Up
Port Up
Port Up
operations: 
Port Up
Port Up
Port Up
Port Up
Port Up
operations: 
Port Up
Port Up
operations: 
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
Port Up
operations: 
Port Up
2019-12-08 20:09:34.266 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:09:34.339 INFO  [n.f.t.TopologyManager] Recomputing topology due to: link-discovery-updates
2019-12-08 20:09:49.271 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:10:04.276 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:10:19.280 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:10:19.383 INFO  [n.f.h.ControllerLogic] [ControllerLogic] Election timed out, setting Controller 1 as LEADER!
2019-12-08 20:10:19.383 INFO  [n.f.h.ControllerLogic] [ControllerLogic] Getting Leader: 1
2019-12-08 20:10:34.284 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:10:49.290 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:11:04.293 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:11:19.297 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:11:34.300 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:11:49.304 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:12:04.307 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:12:19.311 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:12:34.327 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:12:49.330 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:13:04.333 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:13:19.336 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:13:34.338 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:13:49.341 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:14:04.344 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
2019-12-08 20:14:19.346 INFO  [n.f.l.i.LinkDiscoveryManager] Sending LLDP packets out of all the enabled ports
operations: 
Port Down
2019-12-08 20:14:22.900 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=2, dst=00:00:00:00:00:00:00:01, inPort=2, latency=0]
2019-12-08 20:14:22.901 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:01 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=2, latency=0]
operations: 
Link Removed
Link Removed
Port Down
Port Down
operations: 
Port Down
2019-12-08 20:14:23.41 INFO  [n.f.t.TopologyManager] Recomputing topology due to: link-discovery-updates
2019-12-08 20:14:23.65 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:01, port=1, activeSince=Sun Dec 08 20:14:05 EST 2019, lastSeen=Sun Dec 08 20:14:22 EST 2019]]  newmap null 
2019-12-08 20:14:23.66 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:02, port=1, activeSince=Sun Dec 08 20:09:37 EST 2019, lastSeen=Sun Dec 08 20:14:22 EST 2019]]  newmap null 
2019-12-08 20:14:23.134 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=3, dst=00:00:00:00:00:00:00:02, inPort=2, latency=0]
2019-12-08 20:14:23.134 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:02 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=3, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
operations: 
Port Down
CLEARING OTHER THINGS
CLEARING ON DPID: 00:00:00:00:00:00:00:03
2019-12-08 20:14:23.244 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=2
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=4
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=5
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=1
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
2019-12-08 20:14:23.245 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=2
2019-12-08 20:14:23.246 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
2019-12-08 20:14:23.246 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=1
2019-12-08 20:14:23.246 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000000000000/0xffffffffff000000
CLEARING OTHER THINGS
CLEARING ON DPID: 00:00:00:00:00:00:00:03
2019-12-08 20:14:23.246 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=2
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=4
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=5
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=1
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=2
2019-12-08 20:14:23.247 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=1
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000001000000/0xffffffffff000000
CLEARING OTHER THINGS
CLEARING ON DPID: 00:00:00:00:00:00:00:03
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=2
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=4
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:0b, port=5
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=1
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.248 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:03, port=1
2019-12-08 20:14:23.249 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.249 INFO  [n.f.f.Forwarding] src: Removing same-cookie flows to/from DPID=00:00:00:00:00:00:00:04, port=2
2019-12-08 20:14:23.249 INFO  [n.f.f.Forwarding] src: Cookie/mask 0x0020000002000000/0xffffffffff000000
2019-12-08 20:14:23.349 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=4, dst=00:00:00:00:00:00:00:03, inPort=2, latency=0]
2019-12-08 20:14:23.349 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:03 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=4, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
operations: 
Port Down
2019-12-08 20:14:23.515 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=5, dst=00:00:00:00:00:00:00:04, inPort=2, latency=0]
2019-12-08 20:14:23.516 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:04 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=5, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
2019-12-08 20:14:23.567 INFO  [n.f.t.TopologyManager] Recomputing topology due to: link-discovery-updates
2019-12-08 20:14:23.577 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:03, port=1, activeSince=Sun Dec 08 20:09:34 EST 2019, lastSeen=Sun Dec 08 20:14:23 EST 2019]]  newmap null 
2019-12-08 20:14:23.578 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:04, port=1, activeSince=Sun Dec 08 20:09:37 EST 2019, lastSeen=Sun Dec 08 20:14:23 EST 2019]]  newmap null 
operations: 
Port Down
2019-12-08 20:14:23.762 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=6, dst=00:00:00:00:00:00:00:05, inPort=2, latency=0]
2019-12-08 20:14:23.762 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:05 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=6, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
operations: 
Port Down
2019-12-08 20:14:23.974 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=7, dst=00:00:00:00:00:00:00:06, inPort=2, latency=0]
2019-12-08 20:14:23.975 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:06 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=7, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
operations: 
Port Down
2019-12-08 20:14:24.79 INFO  [n.f.t.TopologyManager] Recomputing topology due to: link-discovery-updates
2019-12-08 20:14:24.81 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:06, port=1, activeSince=Sun Dec 08 20:09:34 EST 2019, lastSeen=Sun Dec 08 20:14:22 EST 2019]]  newmap null 
2019-12-08 20:14:24.82 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:07, port=1, activeSince=Sun Dec 08 20:09:34 EST 2019, lastSeen=Sun Dec 08 20:14:22 EST 2019]]  newmap null 
2019-12-08 20:14:24.83 INFO  [n.f.d.i.Device] updateAttachmentPoint: ap [AttachmentPoint [sw=00:00:00:00:00:00:00:05, port=1, activeSince=Sun Dec 08 20:09:34 EST 2019, lastSeen=Sun Dec 08 20:14:22 EST 2019]]  newmap null 
2019-12-08 20:14:24.126 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=8, dst=00:00:00:00:00:00:00:07, inPort=2, latency=0]
2019-12-08 20:14:24.126 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:07 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=8, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
operations: 
Port Down
2019-12-08 20:14:24.308 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:0b outPort=9, dst=00:00:00:00:00:00:00:08, inPort=2, latency=0]
2019-12-08 20:14:24.309 INFO  [n.f.l.i.LinkDiscoveryManager] Inter-switch link removed: Link [src=00:00:00:00:00:00:00:08 outPort=2, dst=00:00:00:00:00:00:00:0b, inPort=9, latency=0]
operations: 
Link Removed
Link Removed
Port Down
operations: 
Port Down
