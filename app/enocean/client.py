#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.internet import protocol

sys.path.insert(0, '..')

import telegram
import devices
import logger


class ClientProtocol(protocol.Protocol):

    def __init__(self, main_server):
        self.main_server = main_server

    def process_telegram(self, t):
        addr = self.transport.getPeer()
        logger.info("EnOcean received telegram from '{}:{}': {}".format(addr.host, addr.port, t))

        telegram_device_id = str(t.sensor_id)

        device = devices.Sensor.objects(device_id=telegram_device_id).first()
        
        if not device:
            #logger.info("Unknown device ID: {}".format(telegram_device_id))
            return
        if device.ignored:
            logger.info("The device ({} - {}) is currently ignored".format(t.sensor_id, t.name))
            return

        device.process_telegram(t, self)

    def dataReceived(self, data):
        #logger.info("EnOcean received data: {}".format(data))

        # Splicing data into 28 characters long packets
        data_packets = [data[i:i + 28] for i in xrange(0, len(data), 28)]
        if len(data_packets[-1]) < 28:
            logger.info('Ignoring incomplete packet: {}'.format(data_packets[-1]))
            del data_packets[-1]
        #logger.info(data_packets)

        for packet in data_packets:
            t = telegram.from_str(packet)
            self.process_telegram(t)


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
