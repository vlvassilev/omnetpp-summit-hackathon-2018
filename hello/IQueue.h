class IQueue
{
    public:
        virtual ~IQueue() { };
        // the current length of the queue
        virtual unsigned int length() = 0;
        // pop a frame.
        virtual void pop() = 0;
};
