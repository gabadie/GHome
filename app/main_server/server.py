#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import reactor

sys.path.insert(0, '..')

import enocean.client


class MainServer(object):

    def __init__(self):
        self.db = mongoengine.connect('tumblelog')
        pass

    def run(self):
        reactor.connectTCP("127.0.0.1", 8000, enocean.client.ClientProtocolFactory(self))
        reactor.run()
