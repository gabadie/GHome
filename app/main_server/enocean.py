#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import sys
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
#from enocean.telegram import Telegram


class Thermometer(model.devices.Thermometer):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def proceed_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()


class ClientProtocol(protocol.Protocol):

    def __init__(self, main_server):
        self.main_server = main_server

    def proceed_telegram(self, telegram):
        print "Telegram: " + telegram

        #if telegram.mode == Telegram.TEACH_IN and not self.is_known(telegram.sensor_id):
        #    self.add_device(Device.from_telegram(self, telegram))

        #elif telegram.mode == Telegram.NORMAL and self.is_known(telegram.sensor_id):
        #    device = self.get_device(telegram.sensor_id)
        #    if not device.ignored:
        #        device.add_reading(telegram)

    def connectionMade(self):
        print "EnOcean connection made"

    def dataReceived(self, data):
        print "EnOcean received data : {}".format(data)


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

