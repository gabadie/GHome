#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc
from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor

sys.path.insert(0, '..')

import logger
import model
import enocean

class Raspi(xmlrpc.XMLRPC):
    def __init__(self):
        self.ip="127.0.0.1"
        self.port=7080
        self.macAddress=""


    ##############Functions added to communicate with the raspi
    #TODO to be completed/modified
    def xmlrpc_add_raspi(self,ip,port,macAddress):
        print "Adding raspi"
        self.ip=ip
        self.port=int(port)
        self.macAddress=macAddress
        return "Added raspi "+str(macAddress)



    #play music with raspby. Here the function is called, url to the music must be generated, and passed to the rasbpi
    # trought play_music(url). On the other side, music will be played. 
    #TODO to be completed
    def xmlrpc_find_music_url(self):
        if self.macAddress=="":
            return "Failed, no raspi registered"
        proxy = Proxy('http://'+ self.ip+':' + str(self.port))
        proxy.callRemote('play_music', ' http://mamusic.mp3')
        reactor.run
        return "Url sent"



class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        xmlrpc.XMLRPC.__init__(self)
        self.main_server = main_server
        self._add_raspi = Raspi()

    def xmlrpc_ping(self, msg):
        logger.info("RpcServer.xmlrpc_ping(\"" + str(msg) + "\")")
        return msg

    # TODO : Remove this? (can't create a generic device, needs args)
    def xmlrpc_create_device(self, device_id, device_name, device_type):
        # Finding the device class
        DeviceClass = [d_class for d_class in model.devices.Device.__subclasses__() if d_class.__name__ == device_type][0]

        d = DeviceClass(device_id=device_id, name=device_name, ignored=False)
        d.save()

        return True

 
