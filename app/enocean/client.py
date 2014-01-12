#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol, task

sys.path.insert(0, '..')

import model
import telegram
import devices
import logger


class ClientProtocol(protocol.Protocol):

    def __init__(self, main_server):
        self.main_server = main_server

    def proceed_telegram(self, t):
        addr = self.transport.getPeer()

        logger.info("EnOcean receive telegram from {}:{}: {}".format(addr.host, addr.port, t))

        if t.mode == telegram.Telegram.TEACH_IN:
            telegram_device_id = str(t.sensor_id)

            device = devices.from_telegram(t)

            if len(model.core.Device.objects(device_id=device.device_id)) != 0:
                logger.info("Device " + str(telegram_device_id) + " already known")

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

    def dataReceived(self, data):
        t = telegram.from_str(data)
        self.proceed_telegram(t)


class ClientProtocolFactory(protocol.ReconnectingClientFactory):

    def __init__(self, main_server):
        self.main_server = main_server
        self.initialDelay = 1
        self.maxDelay = 10
        self.factor = 1.5

    def buildProtocol(self, addr):
        logger.info("EnOcean connection to {}:{} started".format(addr.host, addr.port))

        self.resetDelay()

        return ClientProtocol(self.main_server)

    def clientConnectionFailed(self, connector, reason):
        addr = connector.getDestination()

        logger.info("EnOcean connection to {}:{} failed: {}".format(addr.host, addr.port, reason))

        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        addr = connector.getDestination()

        logger.info("EnOcean connection to {}:{} losted: {}".format(addr.host, addr.port, reason))

        self.retry(connector)
