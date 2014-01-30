#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.internet import protocol

sys.path.insert(0, '..')

import telegram
import devices
import logger
from main_server.server import MainServer
import enocean


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
            logger.info("The device ({}) is currently ignored".format(t.sensor_id))
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

        self.main_server.rpc_server.xmlrpc_bind_devices(1341, 'onclick_top_right', 1348, 'callback_toggle')
        self.main_server.rpc_server.xmlrcp_trigger_event(1341, 'onclick_top_right')

    def send_data(self, data):
        addr = self.transport.getPeer()
        logger.info("EnOcean sends telegram to '{}:{}': {}".format(addr.host, addr.port, t))

        self.transport.write(data)


class ClientProtocolFactory(protocol.ReconnectingClientFactory):

    def __init__(self, main_server):
        self.main_server = main_server
        self.initialDelay = 1
        self.maxDelay = 10
        self.factor = 1.5

    def buildProtocol(self, addr):
        logger.info("EnOcean connection to {}:{} started".format(addr.host, addr.port))

        self.resetDelay()

        enocean_protocol = ClientProtocol(self.main_server)

        self.main_server.enocean_protocol = enocean_protocol

        return enocean_protocol

    def clientConnectionFailed(self, connector, reason):
        addr = connector.getDestination()
        self.main_server.enocean_protocol = None

        logger.info("EnOcean connection to {}:{} failed: {}".format(addr.host, addr.port, reason))

        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        addr = connector.getDestination()

        logger.info("EnOcean connection to {}:{} losted: {}".format(addr.host, addr.port, reason))

        self.retry(connector)
