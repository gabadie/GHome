#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc

sys.path.insert(0, '..')

import logger
import model


class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        xmlrpc.XMLRPC.__init__(self)
        self.main_server = main_server

    def xmlrpc_ping(self, msg):
        logger.info("RpcServer.xmlrpc_ping(\"" + str(msg) + "\")")
        return msg

    def xmlrpc_activate_device(self, device_id, activate):
        if not isinstance(device_id, str):
            return xmlrpc.Fault(1001, "Invalid parameter <device_id>: must be a string.")

        if not isinstance(activate, bool):
            return xmlrpc.Fault(1002, "Invalid parameter <activate>: must be a boolean.")

        devices = model.core.Device.objects(device_id=device_id)

        if len(devices) == 0:
            return xmlrpc.Fault(1201, "Invalid operation: Unknown device id.")

        for d in devices:
            d.ignored = not activate

        return True

    def xmlrpc_create_device(self, device_id, device_name, device_type):
        if not isinstance(device_id, str):
            return xmlrpc.Fault(2001, "Invalid parameter <device_id>: must be a string.")

        if not isinstance(device_name, str):
            return xmlrpc.Fault(2002, "Invalid parameter <device_name>: must be a string.")

        if not isinstance(device_type, classobj):
            return xmlrpc.Fault(2003, "Invalid parameter <device_type>: must be a class.")

        if device_id == "":
            return xmlrpc.Fault(2101, "Invalid parameter <device_id> value: must have at least one character.")

        if not issubclass(device_type, model.core.Device):
            return xmlrpc.Fault(2102, "Invalid parameter <device_type> value: must be a subclass of model.core.Device.")

        if len(model.core.Device.objects(device_id=device_id)) > 0:
            return xmlrpc.Fault(2201, "Invalid operation: {} already exists.".format(device_id))

        d = device_type(device_id=device_id, name=device_name)
        d.save()

        return True
