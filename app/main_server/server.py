#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import os
import sys
from twisted.internet import reactor
import twisted.web

sys.path.insert(0, '..')

import enocean.client
import model.clock
from rpc_server import RpcServer, Raspi
import logger
from config import GlobalConfig
import enocean.devices

class MainServer(object):

    def __init__(self, config):
        self.config = config
        self.db = mongoengine.connect(config.mongo_db)
        self.rpc_server = None
        self.clock_server = None
        self.enocean_protocol = None

        logger.info('main server initialized')

    def run(self):
        logger.info('running main server...')

        """ EnOcean client protocol factory """
        reactor.connectTCP(self.config.enocean.ip, self.config.enocean.port, enocean.client.ClientProtocolFactory(self))

        """ Launchs XML RPC server """
        self.rpc_server = RpcServer(self)
        raspi=Raspi()
        self.rpc_server.putSubHandler('raspi',raspi)
        reactor.listenTCP(self.config.main_server.rpc_port, twisted.web.server.Site(self.rpc_server))

        #switch_id = int("0021CBE5", 16)
        #switch = enocean.devices.Switch(device_id=switch_id, name="THESWITCH", ignored=False)
        #switch.save()

        wc_id = int("0001B592", 16)
        wc = enocean.devices.WindowContact(device_id=wc_id, name="THEWC", ignored=False)
        wc.save()


        socket_id = int("FF9F1E03", 16)
        socket = enocean.devices.Socket(device_id=socket_id, name="THESOCKET", ignored=False)
        socket.save()
        #self.rpc_server.xmlrpc_bind_devices(switch_id, 'onclick_top_right', socket_id, 'callback_toggle')
        self.rpc_server.xmlrpc_bind_devices(wc_id, 'on_opened', socket_id, 'callback_desactivate')
        self.rpc_server.xmlrpc_bind_devices(wc_id, 'on_closed', socket_id, 'callback_activate')


        """ Launchs Clock Server """
        self.clock_server = model.clock.Server(self)

        """ Main loop """
        reactor.run()


if __name__ == "__main__":

    logger.add_file('log/main_server')

    configuration = GlobalConfig()

    if len(sys.argv) > 1:
        configuration = GlobalConfig.from_json(sys.argv[1])

    server = MainServer(configuration)
    server.run()
