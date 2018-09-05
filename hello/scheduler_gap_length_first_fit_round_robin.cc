#include <string.h>
#include <omnetpp.h>
#include "IQueue.h"
using namespace omnetpp;
class scheduler_gap_length_first_fit_round_robin : public cSimpleModule
{
  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};
// The module class needs to be registered with OMNeT++
Define_Module(scheduler_gap_length_first_fit_round_robin);
void scheduler_gap_length_first_fit_round_robin::initialize()
{
}
void scheduler_gap_length_first_fit_round_robin::handleMessage(cMessage *msg)
{
    cGate *gate = this->gate("in2"/*, 0*/)->getPreviousGate();
    check_and_cast<IQueue *>(gate->getOwnerModule())->pop();
    send(msg, "out"); // send out the message
}


