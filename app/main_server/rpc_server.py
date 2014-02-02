#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.web import xmlrpc
import xmlrpclib

sys.path.append('..')
sys.path.append('../../libs/py8tracks/')

from config import GlobalConfig
config = GlobalConfig()

from py8tracks import API8tracks
import logger
from model import devices


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
            server.init_play_music(', '.join(urls))
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

    @staticmethod
    def xmlrpc_bind_devices(sensor_id, sensor_event, actuator_id, actuator_callback):
        sensor = devices.Sensor.objects(device_id=sensor_id).first()
        actuator = devices.Actuator.objects(device_id=actuator_id).first()

        if not sensor or not actuator:
            logger.error("Unknown device when binding {}.{} to {}.{}".format(sensor.__class__, sensor_event, actuator.__class__, actuator_callback))
            return

        connection = sensor.events[sensor_event].connect(actuator.callbacks[actuator_callback])

        return connection.id

    def xmlrcp_trigger_event(self, sensor_id, sensor_event):
        sensor = devices.Sensor.objects(device_id=sensor_id).first()

        if not sensor:
            logger.error("Unknown device when triggering {}.{}".format(sensor_id, sensor_event))
            return

        try:
            getattr(sensor, sensor_event)(self.main_server)
        except AttributeError as ae:
            logger.error("An error occurred when triggering event {}.{} ".format(sensor.__class__.__name__, sensor_event))
            logger.exception(ae)


def search_music_generator(mixset):
    urls=[]
    for mix in mixset.mixes[:1]:
        i=0
        for song in mix:
            if(i<5):
                urls.append(song.data['track_file_stream_url'])# ou track_file_stream_url
                print song.data['track_file_stream_url']
                i+=1
    return urls
