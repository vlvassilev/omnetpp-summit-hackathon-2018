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

    network = tree.xpath(
        '/nc:config/nd:networks[1]/nd:network', namespaces=namespaces)[0]

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
def generate_node_type(node_data, ned_file):
    print("module {}\n{{".format(id_to_type(node_data.id)), file=ned_file)
    print("    gates:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        inout", id_to_name(tp.id) + ";", file=ned_file)

    print("    submodules:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        eth_{}: {};".format(id_to_name(tp.id), "EthernetInterface"), file=ned_file)

    print("    connections:", file=ned_file)

    for tp_id, tp in node_data.termination_points.items():
        print("        {} <--> eth_{}.phys;".format(id_to_name(tp.id), id_to_name(tp.id)), file=ned_file)


    print("}", file=ned_file)
    print("", file=ned_file)


def generate_network_ned(network_data, ned_file_name):
    with open(ned_file_name, "wt") as of:
        print("package simulations;", file=of)
        print("", file=of)
        print("import inet.linklayer.ethernet.EthernetInterface;", file=of)

        print("""
channel EthernetChannel extends ned.DatarateChannel
{
    parameters:
        delay = 0us;
        datarate = 1Gbps;
}
""", file=of)

        for node_id, node in network_data.nodes.items():
            generate_node_type(node, of)

        print("network {}\n{{".format(id_to_type(network_data.id)), file=of)
        print("    submodules:", file=of)

        for node_id, node in network_data.nodes.items():
            print("        {}: {};".format(
                node_id, id_to_type(node_id)), file=of)

        print("    connections:", file=of)

        for link_id, link in network_data.links.items():
            print("        {}.{} <--> EthernetChannel {{ @display(\"t={}\"); }} <--> {}.{};".format(
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
