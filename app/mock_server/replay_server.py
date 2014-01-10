import sys
from twisted.internet import protocol, reactor, task

class ReplayServerProtocol(protocol.Protocol):

    def __init__(self, factory, addr):
        self.factory = factory
        print "New connection : {}".format(addr)

    def connectionMade(self):
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

    def dataReceived(self, data):
        print "Received : {}".format(data)


class ReplayServerProtocolFactory(protocol.Factory):

    def __init__(self, filename):
        self.clients = []
        self.frames  = []
        self.index   = 0

        #with open(filename) as f:
            #self.frames = f.readlines()

        self.frames = [frame.strip() for frame in open(filename)]
        
        if len(self.frames) > 0:
            self.lc = task.LoopingCall(self.replay)
            self.lc.start(1)
        else:
            print "No frame found in \"{}\"".format(filename)

    def buildProtocol(self, addr):
        return ReplayServerProtocol(self, addr)
        
    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

    def replay(self):

        print self.frames[self.index]

        for client in self.clients:
            client.transport.write(self.frames[self.index])

        self.index = (self.index + 1) % len(self.frames)


# How to use it:
#  python ./replay_server [port=8000]
if __name__ == '__main__':

    port = 8000
    framesFilename = "./frames.txt"

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print "Invalid port {} : using default ({})\n".format(sys.argv[1], port)

    print "Replay server sending frames from \"{}\" on port {}\n".format(framesFilename, port)

    reactor.listenTCP(port, ReplayServerProtocolFactory(framesFilename))
    reactor.run()
