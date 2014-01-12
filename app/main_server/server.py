#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import reactor

sys.path.insert(0, '..')

import enocean.client
import logger
import config


class MainServer(object):

    def __init__(self):
        self.db = mongoengine.connect(config.db_name)
        logger.info('main server initialized')
        pass

    def run(self):
        logger.info('running main server...')
        reactor.connectTCP("127.0.0.1", 8000, enocean.client.ClientProtocolFactory(self))
        reactor.run()
