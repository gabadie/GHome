import sys
from twisted.internet import protocol, reactor

class MockClientProtocol(protocol.Protocol):

    def connectionMade(self):
        print "Connection made"

    def dataReceived(self, data):
        print "Received data : {}".format(data)


class MockClientProtocolFactory(protocol.ClientFactory):

    def buildProtocol(self, addr):
        return MockClientProtocol()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed : {}".format(reason)

    def clientConnectionLost(self, connector, reason):
        print "Connection lost"
        reactor.stop()

# How to use it:
#  python ./mock_client.py [port=8000]
if __name__ == '__main__':

    port = 8000

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print "Invalid port {} : using default ({})\n".format(sys.argv[1], port)

    reactor.connectTCP("127.0.0.1", port, MockClientProtocolFactory())
    #reactor.connectTCP("134.214.106.23", 5000, MockClientProtocolFactory())
    reactor.run()
