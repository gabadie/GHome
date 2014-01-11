#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enocean
from twisted.internet import reactor

class MainServer(object):

    def __init__(self):
        pass

    def run(self):
        reactor.connectTCP("127.0.0.1", 8000, enocean.ClientProtocolFactory(self))
        reactor.run()
