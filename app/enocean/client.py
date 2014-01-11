#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
from telegram import Telegram
import devices


class ClientProtocol(protocol.Protocol):

    def __init__(self, main_server):
        self.main_server = main_server

    def proceed_telegram(self, telegram):
        print "EnOcean telegram: " + str(telegram)

        if telegram.mode == Telegram.TEACH_IN:
            device = devices.from_telegram(telegram)

            if len(model.core.Device.objects(device_id=device.device_id)) != 0:
                print "Device " + str(telegram_device_id) + " already known"

            device.save()

            print "EnOcean create device " + device

        elif telegram.mode == Telegram.NORMAL:
            telegram_device_id = str(telegram.sensor_id)

            res = model.core.Device.objects(device_id=telegram_device_id)

            if len(res) == 0:
                print "Unknown device id " + str(telegram_device_id)
                return

            for device in res:
                device.proceed_telegram(telegram)

        else:
            print "Unknown telegram mode"

    def connectionMade(self):
        print "EnOcean connection made"

    def dataReceived(self, data):
        telegram = Telegram.from_str(data)
        self.proceed_telegram(telegram)


class ClientProtocolFactory(protocol.ClientFactory):

    def __init__(self, main_server):
        self.main_server = main_server

    def buildProtocol(self, addr):
        return ClientProtocol(self.main_server)

    def clientConnectionFailed(self, connector, reason):
        print "EnOcean connection failed : {}".format(reason)

    def clientConnectionLost(self, connector, reason):
        print "EnOcean connection lost : {}".format(reason)
        pass

