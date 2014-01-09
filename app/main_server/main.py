#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# tcp : 80,443,4500
# udp : 4500
#

from twisted.internet import protocol, reactor

import server
import device.thermometer
import device.thermometer
import telegram

main_server = MainServer.MainServer()

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

#reactor.listenTCP(1234, EchoFactory())
#reactor.run()

server = MainServer.MainServer()

telegram = Telegram.from_bytes([0xA5, 0x5A, 0x0B, 0x07,
                             0x00, 0x84, 0x99, 0x0F,
                             0x00, 0x04, 0xE9, 0x57, 0x00, 0x01], strict=False)
server.telegram_received(telegram)
server.add_authorized_device(39)

temperatureTelegram = TemperatureTelegram.from_bytes([0xA5, 0x5A, 0x0B, 0x07, 0x00, 0x84, 0x99, 0x0F,
											0x00, 0x04, 0xE9, 0x57, 0x00, 0x01], strict=False)
server.telegram_received(temperatureTelegram)
