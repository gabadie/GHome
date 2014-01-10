from enocean import telegram
from twisted.internet import reactor, protocol, task


raw = [0xA5, 0x5A, 0x0B, 0X07, 0X10, 0x08, 0x02, 0x87, 0x00, 0x04, 0xE9, 0x57, 0x00, 0x88]
T = telegram.Telegram.from_bytes(raw)


class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clientConnectionMade(self)
    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

class MyFactory(protocol.Factory):
    protocol = MyProtocol
    def __init__(self):
        self.clients = []
        self.lc = task.LoopingCall(self.random_telegram)
        self.lc.start(1)

    def random_telegram(self):
        for client in self.clients:
            client.transport.write(str(T))

    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

myfactory = MyFactory()
reactor.listenTCP(9000, myfactory)
reactor.run()