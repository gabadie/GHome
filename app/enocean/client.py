#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
import telegram
import devices
import logger


class ClientProtocol(protocol.Protocol):

    def __init__(self, main_server):
        self.main_server = main_server

    def proceed_telegram(self, t):
        logger.info("EnOcean telegram: " + str(t))

        if t.mode == telegram.Telegram.TEACH_IN:
            telegram_device_id = str(t.sensor_id)

            device = devices.from_telegram(t)

            if len(model.core.Device.objects(device_id=device.device_id)) != 0:
                logger.info("Device " + str(telegram_device_id) + " alreadu known")

            device.save()

            logger.info("EnOcean create device " + device)

        elif t.mode == telegram.Telegram.NORMAL:
            telegram_device_id = str(t.sensor_id)

            res = model.core.Device.objects(device_id=telegram_device_id)

            if len(res) == 0:
                logger.info("Unknown device id " + telegram_device_id)
                return

            for device in res:
                device.proceed_telegram(t)

        else:
            logger.info("Unknown telegram mode")

    def connectionMade(self):
        logger.info("EnOcean connection made")

    def dataReceived(self, data):
        t = telegram.from_str(data)
        self.proceed_telegram(t)


class ClientProtocolFactory(protocol.ClientFactory):

    def __init__(self, main_server):
        self.main_server = main_server

    def buildProtocol(self, addr):
        return ClientProtocol(self.main_server)

    def clientConnectionFailed(self, connector, reason):
        logger.info("EnOcean connection failed : {}".format(reason))

    def clientConnectionLost(self, connector, reason):
        logger.info("EnOcean connection lost : {}".format(reason))
        pass

