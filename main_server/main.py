#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# tcp : 80,443,4500
# udp : 4500
#

from twisted.internet import protocol, reactor

import MainServer

main_server = MainServer.MainServer()

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

#reactor.listenTCP(1234, EchoFactory())
#reactor.run()

