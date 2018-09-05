simple Txc1
{
    gates:
        input in;
        output out;
}
simple traffic_generator
{
    parameters:
        string config = default("<config><traffic-generator><frame-size>64</frame-size><interframe-gap>12</interframe-gap></traffic-generator></config>");
        bool mybool = default(false);
    gates:
        output out;
}
simple delay_line
{
    gates:
        input in;
        output out;
}
simple queue
{
    parameters:
        @signal[dropped](type="long");
        @signal[queueLength](type="long");
        @signal[queueingTime](type="simtime_t");
        @signal[busy](type="bool");
        @statistic[dropped](title="drop event";record=vector?,count;interpolationmode=none);
        @statistic[queueLength](title="queue length";record=vector,timeavg,max;interpolationmode=sample-hold);
        @statistic[queueingTime](title="queueing time at dequeue";record=vector?,mean,max;unit=s;interpolationmode=none);
        @statistic[busy](title="server busy state";record=vector?,timeavg;interpolationmode=sample-hold);

        int capacity = default(-1);    // negative capacity means unlimited queue
        bool fifo = default(true);     // whether the module works as a queue (fifo=true) or a stack (fifo=false)
    gates:
        input in;
        output out;
}
simple traffic_analyzer
{
    gates:
        input in;
}
simple scheduler_gap_length_first_fit_round_robin
{
    gates:
        input in0;
        input in1;
        input in2;
        output out;
}
//
// Two instances (tic and toc) of Txc1 connected both ways.
// Tic and toc will pass messages to one another.
//
network Hello
{
    @display("bgb=930,406");
    submodules:
        ingress0: traffic_generator {
            @display("p=136,27;is=l");
            config = "hue";            
        }
        ingress1: traffic_generator {
            @display("p=225,27;is=l");
        }
        ingress2: traffic_generator {
            @display("p=304,27;is=l");
        }

        delay0: delay_line {
            @display("p=136,127;is=vl;b=40,92,rect");
        }
        queue1: queue {
            @display("p=225,127;is=vl;b=40,92,rect");
        }
        queue2: queue {
            @display("p=304,127;is=vl;b=40,92,rect");
        }
        scheduler0: scheduler_gap_length_first_fit_round_robin {
            @display("p=225,248");
        }
        egress0: traffic_analyzer {
            @display("p=225,327");
        }

    connections:
        ingress0.out --> delay0.in;
        ingress1.out --> queue1.in;
        ingress2.out --> queue2.in;
        delay0.out --> scheduler0.in0;
        queue1.out --> scheduler0.in1;
        queue2.out --> scheduler0.in2;
        scheduler0.out --> egress0.in;
}
