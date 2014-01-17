import argparse, calendar, datetime, sys, time
from twisted.internet import protocol, reactor

class SnifferProtocol(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print "Connection made"

    def dataReceived(self, data):
        self.factory.addFrame(data, datetime.datetime.now())


class SnifferProtocolFactory(protocol.ClientFactory):

    def __init__(self, dumpfile = "dump.txt", dumpFreq = 10):
        self.frames = []
        self.dumpfile = dumpfile
        self.dumpFreq = dumpFreq

    def __del__(self):
        print "Dumping {} remaining frames in {}...".format(len(self.frames), self.dumpfile)
        self.dump()

    def addFrame(self, data, date):
        FRAME_LENGTH = 28
        
        # Split into atomic frames of length FRAME_LENGTH
        atomic_frames = [data[i:i+FRAME_LENGTH] for i in xrange(0, len(data), FRAME_LENGTH)]

        # Remove potential incomplete last frame
        if len(atomic_frames[-1]) < FRAME_LENGTH:
            print "Incomplete frame received : {}".format(atomic_frames[-1])
            del atomic_frames[-1]

        timestamp = calendar.timegm(date.utctimetuple())

        # Save frames
        for frame in atomic_frames:
            print "{} {}".format(datetime.datetime.strftime(date, "[%Y-%m-%d %Hh%Mm%Ss]"), frame)
            self.frames.append((timestamp, frame))
            if len(self.frames) % self.dumpFreq == 0:
                print "Dumping {} frames in \"{}\"".format(self.dumpFreq, self.dumpfile)
                self.dump()


    def buildProtocol(self, addr):
        return SnifferProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed : {}".format(reason)
        if reactor.running: reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost"
        if reactor.running: reactor.stop()
    
    def dump(self):
        with open(self.dumpfile, 'a') as f:
            for (ts, data) in self.frames:
                f.write("{} {}\n".format(ts, data))
            self.frames = []

# How to use it:
#  python ./sniffer.py -h
if __name__ == '__main__':

    # Available args
    parser = argparse.ArgumentParser(description='Sniffer of EnOcean frames.')
    parser.add_argument('-a', dest='address', type=str, nargs=1, help='Gateway\'s address')
    parser.add_argument('-p', dest='port', type=int, nargs=1, help='Gateway\'s port')
    parser.add_argument('-d', dest='dumpfile', type=str, nargs=1, help='Dump filename')
    parser.add_argument('--address', dest='address', type=str, nargs=1, help='Gateway\'s address')
    parser.add_argument('--port', dest='port', type=int, nargs=1, help='Gateway\'s port')
    parser.add_argument('--dumpfile', dest='dumpfile', type=str, nargs=1, help='Dump filename')

    # Parse args
    args = parser.parse_args()

    # Default args
    address = "127.0.0.1"
    port = 8000
    dumpfile = "dump.txt"

    # Retrieve parsed args
    if args.address != None: address = args.address[0]
    if args.port != None: port = args.port[0]
    if args.dumpfile != None: dumpfile = args.dumpfile[0]

    print "Sniffing frames from {}:{} and dumping them in \"{}\"\n".format(address, port, dumpfile)

    reactor.connectTCP(address, port, SnifferProtocolFactory(dumpfile))
    #reactor.connectTCP("134.214.106.23", 5000, SnifferProtocolFactory(dumpfile))
    reactor.run()
