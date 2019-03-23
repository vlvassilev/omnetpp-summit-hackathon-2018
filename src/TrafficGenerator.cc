//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

#include "TrafficGenerator.h"

#include <omnetpp/ccomponent.h>
#include <omnetpp/cexception.h>
#include <omnetpp/clog.h>
#include <omnetpp/cmessage.h>
#include <omnetpp/cnamedobject.h>
#include <omnetpp/cobjectfactory.h>
#include <omnetpp/cpacket.h>
#include <omnetpp/cpar.h>
#include <omnetpp/csimplemodule.h>
#include <omnetpp/cwatch.h>
#include <omnetpp/regmacros.h>
#include <omnetpp/simutil.h>
#include <cstdio>
#include <iostream>
#include <string>

#include "inet/linklayer/common/Ieee802Ctrl.h"

namespace yto {

Define_Module(TrafficGenerator);

void TrafficGenerator::initialize() {
    // Signals
    sentPkSignal = registerSignal("sentPk");

    // Initialize sequence-number for generated packets
    seqNum = 0;

    // NED parameters
    etherType = &par("etherType");
    vlanTagEnabled = &par("vlanTagEnabled");
    pcp = &par("pcp");
    dei = &par("dei");
    vid = &par("vid");
    frameSize = &par("frameSize");
    interFrameGap = &par("interFrameGap");
    const char *destAddress = par("destAddress");
    if (!destMacAddress.tryParse(destAddress)) {
        throw new cRuntimeError("Invalid MAC Address");
    }

    // Statistics
    packetsSent = 0;
    WATCH(packetsSent);

    if (frameSize->intValue() > 0)
        scheduleAt(simTime(), new cMessage("sendNextFrame"));
}

/*
    Ethernet frame-size in octets includes:
    * Destination Address (6 octets),
    * Source Address (6 octets),
    * Frame Type (2 octets),
    * Data (min 46 octets or 42 octets + 4 octets 802.1Q tag),
    * CRC Checksum (4 octets).

    Ethernet frame-size does not include:
    * Preamble (dependent on MAC configuration
            by default 7 octets),
    * Start of frame delimeter (1 octet)
*/

int TrafficGenerator::overheadBytes() {
    // not including preamble and SFD, includes FCS
    return 6 + 6 + (vlanTagEnabled->boolValue() ? 4 : 0) + 2 + /* payload here */ 4;
}

SimTime TrafficGenerator::iaTime() {
    // TODO: take the actual datarate into account
    return SimTime(7 + 1 + frameSize->intValue() + interFrameGap->intValue()) * 8 / 1e9;
}

void TrafficGenerator::handleMessage(cMessage *msg) {
    ASSERT(msg->isSelfMessage());
    scheduleAt(simTime() + iaTime(), msg);
    sendFrame();
}

Packet* TrafficGenerator::makeFrame() {
    seqNum++;

    char msgname[40];
    sprintf(msgname, "pk-%d-%ld", getId(), seqNum);

    // create new packet
    Packet *datapacket = new Packet(msgname, IEEE802CTRL_DATA);

    long payloadLen = frameSize->intValue() - overheadBytes();
    const auto& payload = makeShared<ByteCountChunk>(B(payloadLen));
    // set creation time
    auto timeTag = payload->addTag<CreationTimeTag>();
    timeTag->setCreationTime(simTime());

    datapacket->insertAtBack(payload);
    datapacket->removeTagIfPresent<PacketProtocolTag>();
    datapacket->addTagIfAbsent<PacketProtocolTag>()->setProtocol(
            &Protocol::ipv4);
    // TODO check if protocol is correct
    auto sapTag = datapacket->addTagIfAbsent<Ieee802SapReq>();
    sapTag->setSsap(ssap);
    sapTag->setDsap(dsap);

    auto macTag = datapacket->addTag<MacAddressReq>();
    macTag->setDestAddress(destMacAddress);
    // TODO: src address

    // create VLAN control info
    if (vlanTagEnabled->boolValue()) {
        auto ieee8021q = datapacket->addTag<nesting::VLANTagReq>();
        ieee8021q->setPcp(pcp->intValue());
        ieee8021q->setDe(dei->boolValue());
        ieee8021q->setVID(vid->intValue());
    }
    return datapacket;
}

void TrafficGenerator::sendFrame() {
    Packet* packet = makeFrame();

    if(par("verbose")) {
        auto macTag = packet->findTag<MacAddressReq>();
        auto ieee8021qTag = packet->findTag<nesting::VLANTagReq>();
        EV_TRACE << getFullPath() << ": Send packet `" << packet->getName() << "' dest=" << macTag->getDestAddress()
        << " length=" << packet->getBitLength() << "B type= empty" << " vlan-tagged=false";
        if(ieee8021qTag) {
            EV_TRACE << " vlan-tagged=true" << " pcp=" << ieee8021qTag->getPcp()
            << " dei=" << ieee8021qTag->getDe() << " vid=" << ieee8021qTag->getVID();
        }
        EV_TRACE << endl;
    }
    emit(sentPkSignal, packet);
    send(packet, "out");
    packetsSent++;
}


} // namespace nesting
