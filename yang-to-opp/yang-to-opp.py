import sys
import lxml
import lxml.etree
import json


class Network:
    def __init__(self, id):
        self.id = id
        self.nodes = {}
        self.links = {}


class Node:
    def __init__(self, id):
        self.id = id
        self.termination_points = {}
        self.traffic_generators = []


class TerminationPoint:
    def __init__(self, id):
        self.id = id


class TrafficGenerator:
    def __init__(self, frame_size, interframe_gap, src_address, dst_address):
        self.frame_size = frame_size
        self.interframe_gap = interframe_gap
        self.src_address = src_address
        self.dst_address = dst_address


class Link:
    def __init__(self, id, source_node, source_tp, dest_node, dest_tp):
        self.id = id
        self.source_node = source_node
        self.source_tp = source_tp
        self.dest_node = dest_node
        self.dest_tp = dest_tp


def parse_network_xml(xml_file_name):

    namespaces = {
        "nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
        "nd": "urn:ietf:params:xml:ns:yang:ietf-network",
        "nt": "urn:ietf:params:xml:ns:yang:ietf-network-topology",
        "netconf-acm": "urn:ietf:params:xml:ns:yang:ietf-netconf-acm",
        "netconf-node": "urn:tntapi:netconf-node",
        "tg": "urn:omnetpp:summit:2018:xml:ns:yang:traffic-generator"
    }

    tree = lxml.etree.parse(xml_file_name)

    toplevel = tree.xpath('(/nc:config | /nc:data)', namespaces=namespaces)[0]
    network = toplevel.xpath('nd:networks[1]/nd:network', namespaces=namespaces)[0]

    network_id = network.xpath(
        "nd:network-id/text()", namespaces=namespaces)[0]
    print(network_id)

    network_data = Network(network_id)

    nodes = network.xpath("nd:node", namespaces=namespaces)

    for node in nodes:
        node_id = node.xpath("nd:node-id/text()", namespaces=namespaces)[0]
        print("  " + node_id)

        node_data = Node(node_id)
        network_data.nodes[node_id] = node_data

        termination_points = node.xpath(
            "nt:termination-point", namespaces=namespaces)

        for tp in termination_points:
            tp_id = tp.xpath("nt:tp-id/text()", namespaces=namespaces)[0]
            print("    " + tp_id)

            tp_data = TerminationPoint(tp_id)
            node_data.termination_points[tp_id] = tp_data

        configs = node.xpath("netconf-node:config", namespaces=namespaces)

        if configs:
            config = configs[0]

            traffic_generators = config.xpath(
                "tg:traffic-generator", namespaces=namespaces)

            for traffic_generator in traffic_generators:
                frame_size = traffic_generator.xpath(
                    "tg:frame-size/text()", namespaces=namespaces)[0]
                interframe_gap = traffic_generator.xpath(
                    "tg:interframe-gap/text()", namespaces=namespaces)[0]
                src_address = traffic_generator.xpath(
                    "tg:src-address/text()", namespaces=namespaces)[0]
                dst_address = traffic_generator.xpath(
                    "tg:dst-address/text()", namespaces=namespaces)[0]

                traffic_generator_data = TrafficGenerator(
                    frame_size, interframe_gap, src_address, dst_address)

                node_data.traffic_generators.append(traffic_generator_data)

                print("   ", frame_size, interframe_gap,
                      src_address, dst_address)

    links = network.xpath("nt:link", namespaces=namespaces)

    for link in links:
        link_id = link.xpath("nt:link-id/text()", namespaces=namespaces)[0]
        print("  " + link_id)

        source = link.xpath("nt:source", namespaces=namespaces)[0]
        source_node = source.xpath(
            "nt:source-node/text()", namespaces=namespaces)[0]
        source_tp = source.xpath(
            "nt:source-tp/text()", namespaces=namespaces)[0]

        destination = link.xpath("nt:destination", namespaces=namespaces)[0]
        dest_node = destination.xpath(
            "nt:dest-node/text()", namespaces=namespaces)[0]
        dest_tp = destination.xpath(
            "nt:dest-tp/text()", namespaces=namespaces)[0]

        link_data = Link(link_id, source_node, source_tp, dest_node, dest_tp)

        network_data.links[link_id] = link_data

        print("   ", source_node, source_tp, " -> ", dest_node, dest_tp)

    return network_data


def id_to_name(id):
    return id.lower().replace("-", "_")


def id_to_type(id):
    return "".join([w.title() for w in id.split("-")])


# TODO: deduplicate types for identical nodes?
def generate_host_type(node_data, ned_file, ethernet_datarate):
    print("module {}\n{{".format(id_to_type(node_data.id)), file=ned_file)
    print("    @networkNode;", file=ned_file)
    print("    gates:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        inout", id_to_name(tp.id) + ";", file=ned_file)

    print("    submodules:", file=ned_file)

    traf_gen = node_data.traffic_generators[0] if node_data.traffic_generators else None

    for tp_id, tp in node_data.termination_points.items():
        print("        eth_{}: {} {{ @display(\"p=100,200\"); }};".format(id_to_name(tp.id), "EthernetInterface"), file=ned_file)

        print("        app_{}: {} {{".format(id_to_name(tp.id), "EtherTrafGen"), file=ned_file)
        print("            @display(\"p=100,100\");", file=ned_file)
        if traf_gen:
            print("            // the EtherTrafGen application takes the payload size as parameter, so subtracting the header size", file=ned_file)
            print("            packetLength = {}B - 14B;".format(traf_gen.frame_size), file=ned_file)
            print("            // computing the frame sending time interval based on frame length, interframe gap, and transmission rate. also accounting for the preamble, the SFD, and the FCS", file=ned_file)
            print("            sendInterval = s((7 + 1 + {} + 4 + {})*8 / ({} * 1e6));".format(traf_gen.frame_size, traf_gen.interframe_gap, ethernet_datarate), file=ned_file)
            print("            destAddress = \"{}\";".format(traf_gen.dst_address), file=ned_file)
        else:
            print("            packetLength = 0B;", file=ned_file)
            print("            sendInterval = 0s;", file=ned_file)
        print("        }", file=ned_file)

    print("    connections:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        {} <--> {{ @display(\"m=s\"); }} <--> eth_{}.phys;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)

        print("        eth_{}.upperLayerOut --> app_{}.in;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)
        print("        eth_{}.upperLayerIn <-- app_{}.out;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)


    print("}", file=ned_file)
    print("", file=ned_file)


# TODO: deduplicate types for identical nodes?
def generate_switch_type(node_data, ned_file, ethernet_datarate):
    print("module {}\n{{".format(id_to_type(node_data.id)), file=ned_file)
    print("    parameters:", file=ned_file)
    print("        @networkNode;", file=ned_file)
    print("        @display(\"i=device/switch;bgb={},400\");".format(len(node_data.termination_points)*100 + 300), file=ned_file)
    print("        **.interfaceTableModule = default(\"\");", file=ned_file)

    print("    gates:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        inout {};".format(id_to_name(tp.id)), file=ned_file)

    print("    submodules:", file=ned_file)


    print("""
        relayUnit: <default("ForwardingRelayUnit")> like RelayUnit {{
            @display("p=400,100");
            numberOfPorts = {};
        }}
        clock: <default("IdealClock")> like IClock {{ @display("p=50,50"); }};
        interfaceTable: InterfaceTable {{ @display("p=150,50");}};
        filteringDatabase: FilteringDatabase {{ @display("p=50,150");}};
        scheduleSwap: ScheduleSwap {{ @display("p=150,150");}};
""".format(len(node_data.termination_points)), file=ned_file)

    for i, (tp_id, tp) in enumerate(node_data.termination_points.items()):
        tp_name = id_to_name(tp.id)

        # TODO: group all of this into a "port" compound module?
        print("""
        queuing_{tp_name}: Queuing {{
            @display("p={x1},200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer_{tp_name}.mac";
            gateController.macModule = "^.^.lowerLayer_{tp_name}.mac";
        }}
        lowerLayer_{tp_name}: LowerLayer {{
            @display("p={x2},300");
            mac.queueModule = "^.^.queuing_{tp_name}.transmissionSelection";
            mac.mtu = 1500B;
        }}
""".format(x1=275 + i*100, x2=300 + i*100, tp_name=tp_name), file=ned_file)

    print("    connections:", file=ned_file)

    for i, (tp_id, tp) in enumerate(node_data.termination_points.items()):
        tp_name = id_to_name(tp.id)
        print("""
            lowerLayer_{tp_name}.phys <--> {{ @display("m=s"); }} <--> {tp_name};
            lowerLayer_{tp_name}.upperLayerOut --> relayUnit.in[{i}];
            relayUnit.out[{i}] --> queuing_{tp_name}.in;
            queuing_{tp_name}.eOut --> lowerLayer_{tp_name}.upperLayerEIn;
            queuing_{tp_name}.pOut --> lowerLayer_{tp_name}.upperLayerPIn;
""".format(i=i, tp_name=tp_name), file=ned_file)


    print("}", file=ned_file)
    print("", file=ned_file)


def generate_network_ned(network_data, ned_file_name):

    ethernet_datarate = 1000 # in Mbps

    with open(ned_file_name, "wt") as of:
        print("package yang_to_opp;", file=of)
        print("", file=of)
        print("""import inet.applications.ethernet.EtherTrafGen;
import inet.linklayer.ethernet.EthernetInterface;

import inet.common.queue.Delayer;
import inet.networklayer.common.InterfaceTable;
import nesting.ieee8021q.clock.IClock;
import nesting.ieee8021q.queue.Queuing;
import nesting.ieee8021q.queue.gating.ScheduleSwap;
import nesting.ieee8021q.relay.FilteringDatabase;
import nesting.ieee8021q.relay.RelayUnit;
import nesting.linklayer.LowerLayer;
""", file=of)

        for node_id, node in network_data.nodes.items():
            # TODO: how do we differentiate switches and hosts? do we want to, at all?
            if len(node.termination_points) > 1:
                generate_switch_type(node, of, ethernet_datarate)
            else:
                generate_host_type(node, of, ethernet_datarate)

        print("network {}\n{{".format(id_to_type(network_data.id)), file=of)
        print("    types:",file=of)

        print("""        channel EthernetChannel extends ned.DatarateChannel
        {{
            parameters:
                delay = 0us;
                datarate = {}Mbps;
        }}""".format(ethernet_datarate), file=of)


        print("    submodules:", file=of)

        for node_id, node in network_data.nodes.items():
            print("        {}: {};".format(
                node_id, id_to_type(node_id)), file=of)

        print("    connections:", file=of)

        for link_id, link in network_data.links.items():
            print("        {}.{} <--> EthernetChannel {{ @display(\"t={},l\"); }} <--> {}.{};".format(
                link.source_node, link.source_tp, link_id, link.dest_node, link.dest_tp), file=of)

        print("}", file=of)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("no args")

    network_data = parse_network_xml(sys.argv[1])

    print(json.dumps(network_data, default=lambda obj: vars(
        obj), indent=4, separators=(',', ': ')))

    outfile_name = ""
    if len(sys.argv) < 3:
        outfile_name = sys.argv[1].replace(".xml", ".ned")
    else:
        outfile_name = sys.argv[2]

    generate_network_ned(network_data, outfile_name)
