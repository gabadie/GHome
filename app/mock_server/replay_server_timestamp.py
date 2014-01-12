import sys, time
from twisted.internet import protocol, reactor, threads, task

class Frame:
    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp

    @property
    def data(self):
        return self.data

    @property
    def data(self, data):
        self.data = data

    @property
    def timestamp(self):
        return self.timestamp

    @property
    def timestamp(self, timestamp):
        self.timestamp = timestamp

    def __repr__(self):
        return "[data: {0}, timestamp: {1}]".format(self.data, self.timestamp)


class ReplayServerProtocol(protocol.Protocol):

    def __init__(self, factory, addr):
        self.factory = factory
        print "New connection : {}".format(addr)

    def connectionMade(self):
        self.factory.clientConnectionMade(self)

    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

    def dataReceived(self, data):
        self.transport.write("Received : {}".format(data))
        if data.strip() == "STOP":
            self.factory.stop()


class ReplayServerProtocolFactory(protocol.Factory):

    def __init__(self, filename):
        self.clients = []
        self.frames  = []
        self.index   = 0

        # Parses frames from file
        self.frames = [Frame(f[0], int(f[1])) 
            for f in (frame.strip().split(" ") 
                for frame in open(filename)) if len(f) == 2]

        # Start frames replay in a thread
        if len(self.frames) > 0:
            self.running = True
            self.d = threads.deferToThread(self.replay)
        else:
            print "No frame found in \"{}\"".format(filename)

    def stop(self):
        print "STOPPING..."
        self.running = False

    def buildProtocol(self, addr):
        return ReplayServerProtocol(self, addr)
        
    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

    def replay(self):
        while self.running:
            print self.frames[self.index]

            # Sends frame to connected clients
            for client in self.clients:
                client.transport.write(self.frames[self.index].data)

            # Increments frame index
            oldIndex = self.index
            if(len(self.frames) > 0):
                self.index = (self.index + 1) % len(self.frames)

            # Waits until next frame
            dt = self.frames[self.index].timestamp - self.frames[oldIndex].timestamp
            if dt < 0: dt = 1
    
            # Ugly...
            while dt > 0:
                if not self.running: break
                time.sleep(1)
                dt -= 1

# How to use it:
#  python ./replay_server_timestamp.py [port=8000]
if __name__ == '__main__':

    port = 8000
    framesFilename = "./frames_with_timestamp.txt"

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print "Invalid port {} : using default ({})\n".format(sys.argv[1], port)

    print "Replay server sending frames from \"{}\" on port {}\n".format(framesFilename, port)

    replayServer = ReplayServerProtocolFactory(framesFilename)
    reactor.listenTCP(port, replayServer)
    reactor.addSystemEventTrigger('before', 'shutdown', replayServer.stop)
    reactor.run()
