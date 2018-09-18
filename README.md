# omnetpp-summit-hackathon-2018

## The Plan

This is what was submitted as initial project description:

```
TITLE:
"Deterministic Network Modeling with YANG and Automated Discrete Event System Simulation of the Models with OMNeT++".

BACKGROUND:
With YANG (RFC7950) model of the network topology - ietf-network-topology.yang (RFC8345) one can specify the nodes and the links and by
using model of the nodes ietf-network-bridge-flows.yang (draft) one can specify the behavior of each node part of the network. Network instance
data conforming to the 2 models can be used for simulation run using readily available tools like OMNeT++ if there is tool converting the instance
data file (e.g. my-network-001.xml to my-network-001.ned and C++ implementation of OMNeT++ model conforming to ietf-network-bridge.yang).

GOALS:
1- command line tool that can convert *.xml data conforming to  ietf-network-topology.yang to *.ned,
2- ietf_network_bridge.cc OMNeT++ module implementation of the behavior specified in the ietf-network-bridge.yang model that reads the configuration added as parameter string to the *.ned file.
```

## The deliverables

* setup-hello.sh - script to create the development environment (works without modification on debian stable)
* topology.xml - ietf-network.yang (RFC8345) based description of the simple-example network specified in https://tools.ietf.org/html/draft-vassilev-netmod-network-bridge-00#appendix-A.3
* config-host{0,1,2}.xml - NETCONF configuration of the hosts specifying the pattern of the genrated traffic according to the ./yang/traffic-generator.yang module.
* yang/traffic-generator.yang - module augmenting ietf-interfaces.yang with container specifying basic configuration of traffic generator (source)
* config-br0.xml - NETCONF configuration of the bridge specifying the forwarding rules and trivial scheduler implementation according to the ietf-network-bridge.yang draft module.
* topology-with-config.xml - the topology.xml with all nnetconf ode configurations inserted as <netconf-node:config> containers according to yang/tntapi-netconf-node.yang module.
* simulations/*.{ned|ini} - omnetpp simulation spec files based on INET corresponding to the topology-with-config.xml


## Procedure for adding configuration to the topology

* Dependency {topology.xml,config-br0.xml,config-host0.xml,config-host1.xml,config-host2.xml} -> topology-with-config.xml


## Editing config config-host0.xml
```
shell> echo "<config/>" > config-host0.xml
shell> rm /tmp/ncxserver.sock ; gdb --args /usr/sbin/netconfd  \
--module=/usr/share/yuma/modules/ietf/ietf-network-topology@2018-02-26.yang \
--module=yang/tntapi-netconf-node.yang  \
--module=yang/traffic-generator.yang \
--module=/usr/share/yuma/modules/ietf/ietf-interfaces@2014-05-08.yang \
--module=/usr/share/yuma/modules/ietf/iana-if-type@2014-05-08.yang \
--module=/usr/share/yuma/modules/ietf-draft/ietf-network-bridge.yang \
--module=/usr/share/yuma/modules/ietf-draft/ietf-network-bridge-flows.yang \
--module=/usr/share/yuma/modules/ietf-draft/ietf-network-bridge-scheduler.yang \
--log-level=debug4 \
--superuser=${USER} \
--startup=config-host0.xml
```
yangcli> create /traffic-generator -- dst-address=00:00:00:00:00:02 src-address=00:00:00:00:00:00 frame-size=1514 interframe-gap=12
yangcli> commit
```

## Editing br0 config in yangcli (change config-host0.xml to config-br0.xml when starting the netconfd server)

```
create /bridge/ports/port -- name=p0
create /bridge/ports/port -- name=p1
create /bridge/ports/port -- name=p2
create /interfaces/interface -- name=p0 type=ethernetCsmacd port-name=p0
create /interfaces/interface -- name=p1 type=ethernetCsmacd port-name=p1
create /interfaces/interface -- name=p2 type=ethernetCsmacd port-name=p2
create /flows/flow[id='p0-to-p1'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:00 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:01 match/in-port=p0 actions/action[order='0']/output-action/out-port=p1
create /flows/flow[id='p0-to-p2'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:00 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:02 match/in-port=p0 actions/action[order='0']/output-action/out-port=p2
create /flows/flow[id='p1-to-p0'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:01 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:00 match/in-port=p1 actions/action[order='0']/output-action/out-port=p0
create /flows/flow[id='p1-to-p2'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:01 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:02 match/in-port=p1 actions/action[order='0']/output-action/out-port=p2
create /flows/flow[id='p2-to-p0'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:02 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:00 match/in-port=p2 actions/action[order='0']/output-action/out-port=p0
create /flows/flow[id='p2-to-p1'] -- match/ethernet-match/ethernet-source/address=00:00:00:00:00:02 match/ethernet-match/ethernet-destination/address=00:00:00:00:00:01 match/in-port=p2 actions/action[order='0']/output-action/out-port=p1
create /flows/flow[id='unmatched-from-p0'] -- match/in-port=p0 actions/action[order='0']/output-action/out-port=p1 actions/action[order='1']/output-action/out-port=p2
create /flows/flow[id='unmatched-from-p1'] -- match/in-port=p1 actions/action[order='0']/output-action/out-port=p0 actions/action[order='1']/output-action/out-port=p2
create /flows/flow[id='unmatched-from-p2'] -- match/in-port=p2 actions/action[order='0']/output-action/out-port=p0 actions/action[order='1']/output-action/out-port=p1
commit
```

#Simulating (TODO):
 ./sim_net topology-with-config.xml --sim-time=20 > topology-with-operational-data.xml
