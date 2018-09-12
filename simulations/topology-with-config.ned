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

module Br0
{
    parameters:
        @networkNode;
        @display("i=device/switch;bgb=600,400");
        **.interfaceTableModule = default("");
    gates:
        inout p0;
        inout p1;
        inout p2;
    submodules:

        relayUnit: <default("ForwardingRelayUnit")> like RelayUnit {
            @display("p=400,100");
            numberOfPorts = 3;
        }
        clock: <default("IdealClock")> like IClock { @display("p=50,50"); };
        interfaceTable: InterfaceTable { @display("p=150,50");};
        filteringDatabase: FilteringDatabase { @display("p=50,150");};
        scheduleSwap: ScheduleSwap { @display("p=150,150");};


        queuing_p0: Queuing {
            @display("p=275,200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer_p0.mac";
            gateController.macModule = "^.^.lowerLayer_p0.mac";
        }
        lowerLayer_p0: LowerLayer {
            @display("p=300,300");
            mac.queueModule = "^.^.queuing_p0.transmissionSelection";
            mac.mtu = 1500B;
        }


        queuing_p1: Queuing {
            @display("p=375,200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer_p1.mac";
            gateController.macModule = "^.^.lowerLayer_p1.mac";
        }
        lowerLayer_p1: LowerLayer {
            @display("p=400,300");
            mac.queueModule = "^.^.queuing_p1.transmissionSelection";
            mac.mtu = 1500B;
        }


        queuing_p2: Queuing {
            @display("p=475,200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer_p2.mac";
            gateController.macModule = "^.^.lowerLayer_p2.mac";
        }
        lowerLayer_p2: LowerLayer {
            @display("p=500,300");
            mac.queueModule = "^.^.queuing_p2.transmissionSelection";
            mac.mtu = 1500B;
        }

    connections:

            lowerLayer_p0.phys <--> { @display("m=s"); } <--> p0;
            lowerLayer_p0.upperLayerOut --> relayUnit.in[0];
            relayUnit.out[0] --> queuing_p0.in;
            queuing_p0.eOut --> lowerLayer_p0.upperLayerEIn;
            queuing_p0.pOut --> lowerLayer_p0.upperLayerPIn;


            lowerLayer_p1.phys <--> { @display("m=s"); } <--> p1;
            lowerLayer_p1.upperLayerOut --> relayUnit.in[1];
            relayUnit.out[1] --> queuing_p1.in;
            queuing_p1.eOut --> lowerLayer_p1.upperLayerEIn;
            queuing_p1.pOut --> lowerLayer_p1.upperLayerPIn;


            lowerLayer_p2.phys <--> { @display("m=s"); } <--> p2;
            lowerLayer_p2.upperLayerOut --> relayUnit.in[2];
            relayUnit.out[2] --> queuing_p2.in;
            queuing_p2.eOut --> lowerLayer_p2.upperLayerEIn;
            queuing_p2.pOut --> lowerLayer_p2.upperLayerPIn;

}

module Host0
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface { @display("p=100,200"); };
        app_p0: EtherTrafGen {
            @display("p=100,100");
            // the EtherTrafGen application takes the payload size as parameter, so subtracting the header size
            packetLength = 1514B - 14B;
            // computing the frame sending time interval based on frame length, interframe gap, and transmission rate. also accounting for the preamble, the SFD, and the FCS
            sendInterval = s((7 + 1 + 1514 + 4 + 12)*8 / (1000 * 1e6));
            destAddress = "00:00:00:00:00:02";
        }
    connections:
        p0 <--> { @display("m=s"); } <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
}

module Host1
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface { @display("p=100,200"); };
        app_p0: EtherTrafGen {
            @display("p=100,100");
            packetLength = 0B;
            sendInterval = 0s;
        }
    connections:
        p0 <--> { @display("m=s"); } <--> eth_p0.phys;
        eth_p0.upperLayerOut --> app_p0.in;
        eth_p0.upperLayerIn <-- app_p0.out;
}

module Host2
{
    @networkNode;
    gates:
        inout p0;
    submodules:
        eth_p0: EthernetInterface { @display("p=100,200"); };
        app_p0: EtherTrafGen {
            @display("p=100,100");
            packetLength = 0B;
            sendInterval = 0s;
        }
    connections:
        p0 <--> { @display("m=s"); } <--> eth_p0.phys;
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
        br0: Br0;
        host0: Host0;
        host1: Host1;
        host2: Host2;
    connections:
        host0.p0 <--> EthernetChannel { @display("t=host0.p0-br0.p0,l"); } <--> br0.p0;
        host1.p0 <--> EthernetChannel { @display("t=host1.p0-br0.p1,l"); } <--> br0.p1;
        br0.p2 <--> EthernetChannel { @display("t=br0.p2-host2.p0,l"); } <--> host2.p0;
}
