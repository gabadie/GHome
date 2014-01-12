#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import reactor

sys.path.insert(0, '..')

import enocean.client
import logger


class MainServer(object):

    def __init__(self, config):
        self.config = config
        self.db = mongoengine.connect(config.mongo_db)
        logger.info('main server initialized')

    def run(self):
        logger.info('running main server...')

        reactor.connectTCP(self.config.enocean.ip, self.config.enocean.port, enocean.client.ClientProtocolFactory(self))

        reactor.run()
