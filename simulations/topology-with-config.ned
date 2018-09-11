package yang_to_opp;

import inet.applications.ethernet.EtherTrafGen;
import inet.linklayer.ethernet.EthernetInterface;



import inet.common.queue.Delayer;
import inet.networklayer.common.InterfaceTable;
import nesting.ieee8021q.clock.IClock;
import nesting.ieee8021q.queue.Queuing;
import nesting.ieee8021q.queue.gating.ScheduleSwap;
import nesting.ieee8021q.relay.FilteringDatabase;
import nesting.ieee8021q.relay.RelayUnit;
import nesting.linklayer.LowerLayer;


//
// This module implements an ethernet switch conform to the Ieee802.1Qbv, 
// Ieee802.1Qbu and Ieee802.1Qav standard.
//
// @see ~Queuing, ~LowerLayer, ~RelayUnit, ~FrameAssembler, ~Delayer, ~IClock
// @see ~FilteringDatabase, ~ScheduleSwap
//
module EthernetSwitch_Br0
{
    parameters:
        @networkNode();
        @display("i=device/switch;bgb=,521");
        **.interfaceTableModule = default("");
    gates:
        inout ethg[];
    submodules:
        queuing[sizeof(ethg)]: Queuing {
            @display("p=195,370,r,200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer[" + string(index) + "].mac";
            gateController.macModule = "^.^.lowerLayer[" + string(index) + "].mac";
        }
        lowerLayer[sizeof(ethg)]: LowerLayer {
            mac.queueModule = "^.^.queuing[" + string(index) + "].transmissionSelection";
            mac.mtu = 1500B;
            @display("p=140,440,r,200");
        }
        relayUnit: <default("ForwardingRelayUnit")> like RelayUnit {
            numberOfPorts = sizeof(ethg);
            @display("p=473,165");
        }
        clock: <default("IdealClock")> like IClock {
            @display("p=273,65;is=s");
        }
        filteringDatabase: FilteringDatabase {
            @display("p=73,165;is=s");
        }
        scheduleSwap: ScheduleSwap {
            @display("p=273,165;i=block/switch;is=s");
        }
        interfaceTable: InterfaceTable {
            @display("p=73,65;is=s");
        }

    connections:
        for i=0..sizeof(ethg)-1 {
            lowerLayer[i].phys <--> ethg[i];
            lowerLayer[i].upperLayerOut --> relayUnit.in[i];
            relayUnit.out[i] --> queuing[i].in;
            queuing[i].eOut --> lowerLayer[i].upperLayerEIn;
            queuing[i].pOut --> lowerLayer[i].upperLayerPIn;
        }
}

module Br0
{
    @networkNode;
    gates:
        inout p0;
        inout p1;
        inout p2;
    submodules:
        eth_p0: EthernetInterface;
        app_p0: EtherTrafGen {
            packetLength = 0B;
            sendInterval = 0s;
        }
        eth_p1: EthernetInterface;
        app_p1: EtherTrafGen {
            packetLength = 0B;
            sendInterval = 0s;
        }
        eth_p2: EthernetInterface;
        app_p2: EtherTrafGen {
            packetLength = 0B;
            sendInterval = 0s;
        }
    connections:
        p0 <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
        p1 <--> eth_p1.phys;
        eth_p1.upperLayerOut --> app_p1.in;
        eth_p1.upperLayerIn <-- app_p1.out;
        p2 <--> eth_p2.phys;
        eth_p2.upperLayerOut --> app_p2.in;
        eth_p2.upperLayerIn <-- app_p2.out;
}

module Host0
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface;
        app_p0: EtherTrafGen {
            packetLength = 1514B - 14B;
            sendInterval = s((8 + 1514 + 4 + 12)*8 / (1000 * 1e6));
            destAddress = "00:00:00:00:00:02";
        }
    connections:
        p0 <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
}

module Host1
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface;
        app_p0: EtherTrafGen {
            packetLength = 0B;
            sendInterval = 0s;
        }
    connections:
        p0 <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
}

module Host2
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface;
        app_p0: EtherTrafGen {
            packetLength = 0B;
            sendInterval = 0s;
        }
    connections:
        p0 <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
}

network ExampleNetwork
{
    types:
        channel EthernetChannel extends ned.DatarateChannel
        {
            parameters:
                delay = 0us;
                datarate = 1000Mbps;
        }
    submodules:
        br0: EthernetSwitch_Br0;
        host0: Host0;
        host1: Host1;
        host2: Host2;
    connections:
        host0.p0 <--> EthernetChannel { @display("t=host0.p0-br0.p0"); } <--> br0.ethg++;
        host1.p0 <--> EthernetChannel { @display("t=host1.p0-br0.p1"); } <--> br0.ethg++;
        br0.ethg++ <--> EthernetChannel { @display("t=br0.p2-host2.p0"); } <--> host2.p0;
}
