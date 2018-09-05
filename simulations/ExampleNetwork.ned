package simulations;


import inet.node.ethernet.EtherSwitch;
import ned.DatarateChannel;
import src.ExampleHost;


network ExampleNetwork
{
    @display("bgb=437,271");
    types:
        channel ethernetline extends DatarateChannel
        {
            parameters:
                delay = 0us;
                datarate = 1Gbps;
        }
    submodules:
        host2: ExampleHost {
            parameters:
                @display("p=162,206");
        }
        host1: ExampleHost {
            parameters:
                @display("p=279,125");
        }
        host0: ExampleHost {
            parameters:
                @display("p=58,125");
        }
        br0: EtherSwitch {
            parameters:
                @display("p=162,124");
                csmacdSupport = false;
            gates:
                ethg[];
        }
    connections:
        br0.ethg++ <--> ethernetline <--> host0.ethg;
        br0.ethg++ <--> ethernetline <--> host1.ethg;
        br0.ethg++ <--> ethernetline <--> host2.ethg;
}
