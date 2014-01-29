#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc
import xmlrpclib


#from SimpleXMLRPCServer import SimpleXMLRPCServer
#from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


sys.path.insert(0, '..')
sys.path.insert(0, '../../libs/py8tracks')

from config import GlobalConfig
config = GlobalConfig()

from py8tracks import API8tracks
import logger
import model



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
            print tags_low
            mixset = api.mixset(tags=tags_low, sort='popular')
            urls=search_music_generator(mixset)
            print "http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port)
            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            server.init_play_music(urls)
        else :
            return "Failed, no raspi get this ID"
        return urls

    def xmlrpc_next_music(self, id):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"

            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            server.next_music()
        else :
            return "Failed, no raspi get this ID"
        return "next music playing"

    def xmlrpc_previous_music(self, id):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"

            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            server.previous_music()
        else :
            return "Failed, no raspi get this ID"
        return "previous music playing"

    def xmlrpc_pause_music(self, id):
        print "server reached"
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"

            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            result = server.pause_music()
        else :
            return "Failed, no raspi get this ID"
        return result




class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        xmlrpc.XMLRPC.__init__(self)
        self.main_server = main_server
        raspi = Raspi()
        self.putSubHandler('raspi',raspi)

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
    urls=[]
    for mix in mixset.mixes:
        for song in mix:
            urls= song.data['url']# ou track_file_stream_url
            print urls
            return urls