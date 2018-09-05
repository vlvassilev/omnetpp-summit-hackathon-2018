#include <string.h>
#include <omnetpp.h>
#include "IQueue.h"
using namespace omnetpp;
class queue : public cSimpleModule, public IQueue
{

  private:
    int capacity;
    simsignal_t droppedSignal;
    simsignal_t queueLengthSignal;
    cQueue queue;
  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
    // external control methods:
    virtual unsigned int length() override;
    virtual void pop() override;
};
// The module class needs to be registered with OMNeT++
Define_Module(queue);
void queue::initialize()
{
    droppedSignal = registerSignal("dropped");
    queueLengthSignal = registerSignal("queueLength");
    emit(queueLengthSignal, 0);
    capacity = par("capacity");
}
void queue::handleMessage(cMessage *msg)
{

    // check for container capacity
    if (capacity >= 0 && queue.getLength() >= capacity) {
        EV << "Queue full! Job dropped.\n";
        if (hasGUI())
            bubble("Dropped!");
        emit(droppedSignal, 1);
        delete msg;
        return;
    }
    queue.insert(msg);
    emit(queueLengthSignal, queue.getLength());
}

unsigned int queue::length()
{
    return queue.getLength();
}

void queue::pop()
{
    Enter_Method("request()!");
    send((cMessage *)queue.pop(), "out"); // send out the message
    emit(queueLengthSignal, queue.getLength());
}
