from queue import Queue
from threading import Thread

# Object that signals shutdown
_sentinel = object()


# A thread that produces data
def producer(out_q):
    while True:
        # Produce some data
        data = input("Data: ")

        if data == "z":
            break

        out_q.put(data)

    # Put the sentinel on the queue to indicate completion
    out_q.put(_sentinel)


# A thread that consumes data
def consumer(in_q):
    while True:
        # Get some data
        data = in_q.get()

        # Check for termination
        if data is _sentinel:
            in_q.put(_sentinel)
            break

        print(data)


# Create the shared queue and launch both threads
q = Queue()
t1 = Thread(target=consumer, args=(q, ))
t2 = Thread(target=producer, args=(q, ))
t1.start()
t2.start()


