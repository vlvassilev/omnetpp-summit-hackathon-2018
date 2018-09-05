#include <string.h>
#include <omnetpp.h>

#include <stdint.h>
extern "C"
{
#include "libtraffic.h"
}

#include "packet_m.h"

using namespace omnetpp;

static void byte_to_hexchar(unsigned char byte, char* hexchar_high, char* hexchar_low)
{
    unsigned char quad_high;
    unsigned char quad_low;

    quad_high = (byte >>4)&0xF;
    quad_low = (byte)&0xF;

    /* hexstr.h:31: warning: comparison is always true due to limited range of data type */
    if(/*quad_high>=0 && */ quad_high<=9) {
        *hexchar_high = quad_high+'0';
    } else if (quad_high>=0xA && quad_high<=0xF) {
        *hexchar_high = quad_high+'A'-10;
    }

    /* hexstr.h:38: warning: comparison is always true due to limited range of data type */
    if(/*quad_low>=0 && */ quad_low<=9) {
        *hexchar_low = quad_low+'0';
    } else if (quad_low>=0xA && quad_low<=0xF) {
        *hexchar_low = quad_low+'A'-10;
    }

}
static void byte_array_to_hexchar_array(const unsigned char* byte_array, char* hexstr, unsigned int bytes_num)
{
    unsigned int i;

    for(i=0;i<bytes_num;i++) {
        byte_to_hexchar(byte_array[i], &hexstr[i*2],&hexstr[i*2+1]);
    }
    hexstr[i*2]=0;
}


class traffic_generator : public cSimpleModule
{
  private:
    traffic_generator_instance_t tg_id;
  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};
// The module class needs to be registered with OMNeT++
Define_Module(traffic_generator);
void traffic_generator::initialize()
{
    // Initialize is called at the beginning of the simulation.
    // To bootstrap the tic-toc-tic-toc process, one of the modules needs
    // to send the first message. Let this be `tic'.
    // Am I Tic or Toc?
    //if (strcmp("tic", getName()) == 0) {
        // create and send first message on gate "out". "tictocMsg" is an
        // arbitrary string which will be the name of the message object.
//        cMessage *msg = new cMessage(par("config").stringValue());
//        send(msg, "out");
    //}
    uint64_t tx_time_sec;
    uint32_t tx_time_nsec;
    int res;
    uint32_t len;
    uint8_t* data;
    char* data_hex;
    tg_id=traffic_generator_init(par("config").stringValue());
    res=traffic_generator_get_frame(tg_id, &len, &data, &tx_time_sec, &tx_time_nsec);
    printf("len=%d\n",len);
    data_hex=(char*)malloc(2*len+1);
    byte_array_to_hexchar_array(data,data_hex,len);
    //cMessage *msg = new cMessage(data_hex);
    Packet *pkt = new Packet("blah");
    pkt->setData((const char*)data_hex);
    free(data);
    free(data_hex);
    scheduleAt((double)tx_time_sec+ ((double)tx_time_nsec)/1000000000, pkt);

}

void traffic_generator::handleMessage(cMessage *msg)
{
    // The handleMessage() method is called whenever a message arrives
    // at the module. Here, we just send it to the other module, through
    // gate `out'. Because both `tic' and `toc' does the same, the message
    // will bounce between the two.
    send(msg, "out"); // send out the message

    uint64_t tx_time_sec;
    uint32_t tx_time_nsec;
    int res;
    uint32_t len;
    uint8_t* data;
    char* data_hex;
    res=traffic_generator_get_frame(tg_id, &len, &data, &tx_time_sec, &tx_time_nsec);
    printf("len=%d\n",len);
    data_hex=(char*)malloc(2*len+1);
    byte_array_to_hexchar_array(data,data_hex,len);
    //cMessage *msg = new cMessage(data_hex);
    Packet *pkt = new Packet("blah");
    pkt->setData((const char*)data_hex);
    free(data);
    free(data_hex);
    scheduleAt((double)tx_time_sec+ ((double)tx_time_nsec)/1000000000, pkt);

}
