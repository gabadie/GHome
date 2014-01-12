#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import reactor
import twisted.web

sys.path.insert(0, '..')

import enocean.client
import logger
from rpc_server import RpcServer


class MainServer(object):

    def __init__(self, config):
        self.config = config
        self.db = mongoengine.connect(config.mongo_db)
        self.rpc_server = None

        logger.info('main server initialized')

    def run(self):
        logger.info('running main server...')

        """ EnOcean client protocol factory """
        reactor.connectTCP(self.config.enocean.ip, self.config.enocean.port, enocean.client.ClientProtocolFactory(self))

        """ Launchs XML RPC server """
        self.rpc_server = RpcServer(self)
        reactor.listenTCP(self.config.main_server.rpc_port, twisted.web.server.Site(self.rpc_server))

        """ Main loop """
        reactor.run()
