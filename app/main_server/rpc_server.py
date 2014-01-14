#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc

sys.path.insert(0, '..')

import logger
import model
import enocean


class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        xmlrpc.XMLRPC.__init__(self)
        self.main_server = main_server

    def xmlrpc_ping(self, msg):
        logger.info("RpcServer.xmlrpc_ping(\"" + str(msg) + "\")")
        return msg

    # TODO : Remove this? (can't create a generic device, needs args)
    def xmlrpc_create_device(self, device_id, device_name, device_type):
        # Finding the device class
        DeviceClass = [d_class for d_class in model.core.Device.__subclasses__() if d_class.__name__ == device_type][0]

        d = DeviceClass(device_id=device_id, name=device_name, ignored=False)
        d.save()

        return True
