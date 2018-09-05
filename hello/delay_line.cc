#include <string.h>
#include <omnetpp.h>
using namespace omnetpp;
class delay_line : public cSimpleModule
{
  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};
// The module class needs to be registered with OMNeT++
Define_Module(delay_line);
void delay_line::initialize()
{
    // Initialize is called at the beginning of the simulation.
    // To bootstrap the tic-toc-tic-toc process, one of the modules needs
    // to send the first message. Let this be `tic'.
    // Am I Tic or Toc?
    //if (strcmp("tic", getName()) == 0) {
        // create and send first message on gate "out". "tictocMsg" is an
        // arbitrary string which will be the name of the message object.
        //cMessage *msg = new cMessage("tictocMsg");
        //send(msg, "out");
    //}
}
void delay_line::handleMessage(cMessage *msg)
{
    // The handleMessage() method is called whenever a message arrives
    // at the module. Here, we just send it to the other module, through
    // gate `out'. Because both `tic' and `toc' does the same, the message
    // will bounce between the two.

    printf("delay: %d\n",(unsigned int)msg->getKind());
    if(msg->getKind()==0) {
        msg->setKind(1);
        scheduleAt(msg->getArrivalTime()+((float)1000)/1000000000 /*1000 ns*/, msg);
    } else {
        msg->setKind(0);
        send(msg, "out"); // send out the message
    }

}
