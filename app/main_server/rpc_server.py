#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc

sys.path.insert(0, '..')

import logger


class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        self.main_server = main_server

    def xmlrpc_ping(self, msg):
        logger.info("RpcServer.xmlrpc_ping(\"" + str(msg) + "\")")
        return msg
