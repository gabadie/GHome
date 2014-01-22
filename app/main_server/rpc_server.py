#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc
from twisted.web.xmlrpc import Proxy
from twisted.internet import reactor
import xmlrpclib

from config import GlobalConfig
config = GlobalConfig()

#from SimpleXMLRPCServer import SimpleXMLRPCServer
#from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


sys.path.insert(0, '..')
sys.path.insert(0, '../../libs/py8tracks')

from py8tracks import API8tracks
import logger
import model
import enocean


class RaspiUnit(object):
    def __init__(self):
        self.ip="127.0.0.1"
        self.macAddress=""
        self.port = 7080

class Raspi(xmlrpc.XMLRPC):
    def __init__(self):
        self.rpi= list() 


    ##############Functions added to communicate with the raspi
    #TODO to be completed/modified
    def xmlrpc_add_raspi(self,ip,port,macAddress):
        print "Adding raspi ip: " + str(ip) + "port: "+ str(port) + "Mac Address: " + macAddress
        self.rpi.append(RaspiUnit())
        id=len(self.rpi)-1
        self.rpi[id].ip=ip
        self.rpi[id].port=int(port)
        self.rpi[id].macAddress=macAddress
        return id



    #play music with raspby. Here the function is called, url to the music must be generated, and passed to the rasbpi
    # trought play_music(url). On the other side, music will be played. 
    #TODO to be completed
    def xmlrpc_find_music_url(self, id, tags ):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"

            api=API8tracks(config.api_8tracks)
            tags_low=[tag.lower() for tag in tags]
            print tags
            mixset = api.mixset(tags=tags_low, sort='popular')
            url=search_music_generator(mixset)


            server = xmlrpclib.Server("http://"+ self.rpi[0].ip+':' + str(self.rpi[id].port))
            server.play_music(next(url))
            #proxy = Proxy('http://'+ self.rpi[0].ip+':' + str(self.rpi[id].port))
        else :
            return "Failed, no raspi get this ID"
        #proxy.callRemote('play_music', url)
        #reactor.run
        return "Url sent"
    #server.register_function(adder_function, 'add')



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

 
def search_music_generator(mixset):
    for mix in mixset.mixes:
        for song in mix:
            yield song.data['url']# ou track_file_stream_url