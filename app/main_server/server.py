#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import os
import sys
from twisted.internet import reactor
import twisted.web

sys.path.insert(0, '..')

import enocean.client
from rpc_server import RpcServer, Raspi


class MainServer(object):

    instance = None

    def __init__(self, config):
        self.config = config
        self.db = mongoengine.connect(config.mongo_db)
        print config.mongo_db
        self.rpc_server = None

        logger.info('main server initialized')

        MainServer.instance = self

    def run(self):
        logger.info('running main server...')

        """ EnOcean client protocol factory """
        reactor.connectTCP(self.config.enocean.ip, self.config.enocean.port, enocean.client.ClientProtocolFactory(self))

        """ Launchs XML RPC server """
        self.rpc_server = RpcServer(self)
        raspi=Raspi()
        self.rpc_server.putSubHandler('raspi',raspi)
        reactor.listenTCP(self.config.main_server.rpc_port, twisted.web.server.Site(self.rpc_server))

        """ Main loop """
        reactor.run()


if __name__ == "__main__":
    import logger
    from config import GlobalConfig

    logger.add_file('log/main_server')

    configuration = GlobalConfig()

    if len(sys.argv) > 1:
        configuration = GlobalConfig.from_json(sys.argv[1])

    server = MainServer(configuration)
    server.run()
