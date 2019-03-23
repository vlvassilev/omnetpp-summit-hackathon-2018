#!/usr/bin/env python3

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
        self.interfaces = {}
        self.traffic_generators = []
        self.flows = {}

class TerminationPoint:
    def __init__(self, id):
        self.id = id

class Interface:
    def __init__(self, name, address):
        self.name = name
        self.address = address

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

class Flow:
    def __init__(self, id, in_port, eth_src, eth_dest, out_port):
        self.id = id
        self.in_port = in_port
        self.eth_src = eth_src
        self.eth_dest = eth_dest
        self.out_port = out_port


def parse_network_xml(xml_file_name):

    namespaces = {
        "nc": "urn:ietf:params:xml:ns:netconf:base:1.0",
        "nd": "urn:ietf:params:xml:ns:yang:ietf-network",
        "nt": "urn:ietf:params:xml:ns:yang:ietf-network-topology",
        "netconf-acm": "urn:ietf:params:xml:ns:yang:ietf-netconf-acm",
        "netconf-node": "urn:tntapi:netconf-node",
        "fl": "urn:ietf:params:xml:ns:yang:ietf-network-bridge-flows",
        "tg": "urn:omnetpp:summit:2018:xml:ns:yang:traffic-generator",
        "if": "urn:ietf:params:xml:ns:yang:ietf-interfaces",
        "ift": "urn:ietf:params:xml:ns:yang:iana-if-type",
        "eth": "urn:ietf:params:xml:ns:yang:ietf-interfaces-ethernet-like",
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


            interfaces = config.xpath(
                "if:interfaces/if:interface", namespaces=namespaces)

            for interface in interfaces:
                name = interface.xpath("if:name/text()", namespaces=namespaces)
                address = interface.xpath(
                    "eth:ethernet-like/eth:mac-address/text()", namespaces=namespaces)

                if name and address:
                    interface_data = Interface(name[0], address[0])
                    node_data.interfaces[name[0]] = interface_data
                    print("   ", name[0], address[0])


            flows = config.xpath(
                "fl:flows/fl:flow", namespaces=namespaces)

            for flow in flows:
                flow_id = flow.xpath("fl:id/text()", namespaces=namespaces)[0]

                in_port = flow.xpath("fl:match/fl:in-port/text()", namespaces=namespaces)[0]

                eth_src = flow.xpath("fl:match/fl:ethernet-match/fl:ethernet-source/fl:address/text()", namespaces=namespaces)
                eth_dest = flow.xpath("fl:match/fl:ethernet-match/fl:ethernet-destination/fl:address/text()", namespaces=namespaces)

                out_port = flow.xpath("fl:actions/fl:action/fl:output-action/fl:out-port/text()", namespaces=namespaces)[0]

                if eth_src and eth_dest:
                    flow_data = Flow(flow_id, in_port, eth_src[0], eth_dest[0], out_port)

                    print("   ", in_port, eth_src[0], eth_dest[0], out_port)

                    node_data.flows[flow_id] = flow_data

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
    print("    parameters:", file=ned_file)
    print("        @networkNode;", file=ned_file)
    print("        **.interfaceTableModule = default(\"\");", file=ned_file)
    print("        **.registerProtocol = true;", file=ned_file)

    for intf_name, intf in node_data.interfaces.items():
        print("        eth_{}.address = \"{}\";".format(intf.name, intf.address), file=ned_file)

    print("    gates:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        inout", id_to_name(tp.id) + ";", file=ned_file)

    print("    submodules:", file=ned_file)

    traf_gen = node_data.traffic_generators[0] if node_data.traffic_generators else None

    for tp_id, tp in node_data.termination_points.items():
        print("        eth_{}: {} {{".format(id_to_name(tp.id), "VLANEthernetInterfaceHost"), file=ned_file)
        print("            @display(\"p=100,200\");", file=ned_file)
        if traf_gen:
            print("            mac.queueModule = \"^.^.gen_{}\";".format(id_to_name(tp.id)), file=ned_file)
        print("        };", file=ned_file)

        print("        encap_{}: {} {{ @display(\"p=100,150\"); }};".format(id_to_name(tp.id), "VLANEncap"), file=ned_file)

        print("        sink_{}: {};".format(id_to_name(tp.id), "Sink"), file=ned_file)
        print("        gen_{}: {} {{".format(id_to_name(tp.id), "TrafficGenerator"), file=ned_file)
        print("            @display(\"p=100,100\");", file=ned_file)
        if traf_gen:
            print("            packetLength = {}B - 18B;".format(traf_gen.frame_size), file=ned_file)
            print("            // computing the frame sending time interval based on frame length, interframe gap, and transmission rate. also accounting for the preamble, the SFD, and the FCS", file=ned_file)
            print("            // sendInterval = s((7 + 1 + {} + 4 + {})*8 / ({} * 1e6));".format(traf_gen.frame_size, traf_gen.interframe_gap, ethernet_datarate), file=ned_file)
            print("            destAddress = \"{}\";".format(traf_gen.dst_address), file=ned_file)
            print("            etherType = 2048;", file=ned_file)
            print("            pcp = 5;", file=ned_file)
            print("            vlanTagEnabled = true;", file=ned_file)
        else:
            print("            destAddress = \"00:00:00:00:00:00\";", file=ned_file)
            print("            packetLength = 10B;", file=ned_file)
            print("            // sendInterval = 0s;", file=ned_file)

        print("        }", file=ned_file)

    print("    connections:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        encap_{}.upperLayerOut --> sink_{}.in++;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)
        print("        encap_{}.upperLayerIn <-- gen_{}.out;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)

        print("        eth_{}.upperLayerOut --> encap_{}.lowerLayerIn;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)
        print("        eth_{}.upperLayerIn <-- encap_{}.lowerLayerOut;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)

        print("        {} <--> {{ @display(\"m=s\"); }} <--> eth_{}.phys;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)

    print("}", file=ned_file)
    print("", file=ned_file)


# TODO: deduplicate types for identical nodes?
def generate_switch_type(node_data, ned_file, ethernet_datarate):
    print("module {}\n{{".format(id_to_type(node_data.id)), file=ned_file)
    print("    parameters:", file=ned_file)
    print("        @networkNode;", file=ned_file)
    print("        @display(\"i=device/switch;bgb={},400\");\n".format(len(node_data.termination_points)*100 + 300), file=ned_file)
    print("        **.interfaceTableModule = default(\"\");", file=ned_file)
    print("        **.registerProtocol = true;", file=ned_file)

    print("""        filteringDatabase.database = xml(" \\""", file=ned_file)
    print("""            <filteringDatabases><filteringDatabase id=\\"{}\\"> \\""".format(id_to_name(node_data.id)), file=ned_file)
    print("""                <static><forward> \\""", file=ned_file)

    for flow_id, flow in node_data.flows.items():
        ifs = list(node_data.termination_points.keys())
        out_port = ifs.index(flow.out_port)

        print("""                    <individualAddress macAddress=\\"{}\\" port=\\"{}\\" /> \\""".format(flow.eth_dest, out_port), file=ned_file)

    print("""                </forward></static> \\""", file=ned_file)
    print("""            </filteringDatabase></filteringDatabases>");\n""", file=ned_file)

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
        processingDelay_{tp_name}: Delayer {{
            @display("p={x1},200");
            tsAlgorithms[*].macModule = "^.^.lowerLayer_{tp_name}.mac";
            gateController.macModule = "^.^.lowerLayer_{tp_name}.mac";
        }}
        eth_{tp_name}: VLANEthernetInterfaceSwitchPreemptable {{
            @display("p={x2},300");
            mac.queueModule = "^.^.eth_{tp_name}.queuing.transmissionSelection";
            **.tsAlgorithms[*].macModule = "^.^.^.eth_{tp_name}.mac";
            **.gateController.macModule = "^.^.^.eth_{tp_name}.mac";
            mac.mtu = 1500B;
            mac.promiscuous = true;

            mac.enablePreemptingFrames = false;
        }}
""".format(x1=275 + i*100, x2=300 + i*100, tp_name=tp_name), file=ned_file)

    print("    connections:", file=ned_file)

    for i, (tp_id, tp) in enumerate(node_data.termination_points.items()):
        tp_name = id_to_name(tp.id)
        print("""
            eth_{tp_name}.phys <--> {{ @display("m=s"); }} <--> {tp_name};
            eth_{tp_name}.upperLayerOut --> processingDelay_{tp_name}.in;
            processingDelay_{tp_name}.out --> relayUnit.in[{i}];
            relayUnit.out[{i}] --> eth_{tp_name}.upperLayerIn;
""".format(i=i, tp_name=tp_name), file=ned_file)


    print("}", file=ned_file)
    print("", file=ned_file)


def generate_network_ned(network_data, ned_file_name):

    ethernet_datarate = 1000 # in Mbps

    with open(ned_file_name, "wt") as of:
        print("""
import inet.common.queue.Delayer;
import inet.common.queue.Sink;
import inet.networklayer.common.InterfaceTable;
import nesting.ieee8021q.clock.IClock;
import nesting.ieee8021q.queue.Queuing;
import nesting.ieee8021q.queue.gating.ScheduleSwap;
import nesting.ieee8021q.relay.FilteringDatabase;
import nesting.ieee8021q.relay.RelayUnit;
import nesting.linklayer.ethernet.VLANEncap;
import yto.TrafficGenerator;
import nesting.node.ethernet.VLANEthernetInterfaceSwitchPreemptable;
import nesting.node.ethernet.VLANEthernetInterfaceHost;
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
