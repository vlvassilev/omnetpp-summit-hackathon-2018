package yang_to_opp;

import inet.applications.ethernet.EtherAppCli;
import inet.applications.ethernet.EtherAppSrv;
import inet.linklayer.contract.IEtherMAC;
import inet.linklayer.ethernet.EtherLLC;

//
// An example host with one Ethernet port and a traffic generator that
// generates traffic directly over Ethernet. This host model
// does not contain higher layer protocols (IP, TCP)-
//
module ExampleHost
{
    parameters:
        string macType = "EtherMACFullDuplex";
        @networkNode();
        @labels(node,ethernet-node);
        @display("i=device/pc2");
        *.interfaceTableModule = default("");
    gates:
        inout ethg @labels(EtherFrame-conn);
    submodules:
        cli: EtherAppCli {
            parameters:
                registerSAP = true;
                @display("p=120,58,col");
        }
        srv: EtherAppSrv {
            parameters:
                registerSAP = true;
                @display("p=310,58,col");
        }
        llc: EtherLLC {
            parameters:
                @display("p=215,118");
            gates:
                upperLayerIn[2];
                upperLayerOut[2];
        }
        mac: <macType> like IEtherMAC {
            parameters:
                queueModule = "";
                @display("p=215,270;q=txQueue");
        }
    connections:

        cli.out --> llc.upperLayerIn[0];
        cli.in <-- llc.upperLayerOut[0];
        srv.out --> llc.upperLayerIn[1];
        srv.in <-- llc.upperLayerOut[1];

        llc.lowerLayerOut --> mac.upperLayerIn;
        mac.upperLayerOut --> llc.lowerLayerIn;

        mac.phys <--> ethg;
}
