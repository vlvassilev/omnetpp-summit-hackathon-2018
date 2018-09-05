# omnetpp-summit-hackathon-2018

#Procedure for adding configuration to the topology {topology.xml,config-br0.xml,config-host0.xml,config-host1.xml,config-host2.xml} -> topology-with-config.xml

#Simulating:
 ./sim_net topology-with-config.xml --sim-time=20 > topology-with-operational-data.xml

#Editing configs: e.g. config-host0.xml
1> echo "<config/>" > config-host0.xml
1> rm /tmp/ncxserver.sock ; gdb --args /usr/sbin/netconfd  --module=/usr/share/yuma/modules/ietf/ietf-network-topology@2018-02-26.yang --module=yang/tntapi-netconf-node.yang  --module=yang/traffic-generator.yang --log-level=debug4 --startup=config-host0.xml

yangcli> create /traffic-generator -- dst-address=00:00:00:00:00:02 src-address=00:00:00:00:00:00 frame-size=1514 interframe-gap=12
yangcli> commit
