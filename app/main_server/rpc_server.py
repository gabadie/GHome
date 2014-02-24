#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from twisted.web import xmlrpc
import xmlrpclib
import requests
import json
import mongoengine
#from SimpleXMLRPCServer import SimpleXMLRPCServer
#from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../../libs/py8tracks/'))

from config import GlobalConfig
config = GlobalConfig()

from py8tracks import API8tracks
import logger
import model.event
from model import devices
from model.event import Connection
from model.phone import Phone

class RaspiUnit(model.devices.Actuator):
    name = mongoengine.StringField(default = "rpi")
    ip=mongoengine.StringField(default = "127.0.0.1")
    macAddress= mongoengine.StringField(default = "")
    port = mongoengine.IntField(default = 7080)


    def callback_rpi_music(self,server):
        tags=["happy"]
        api=API8tracks(config.api_8tracks)
        tags_low=[tag.lower() for tag in tags]
        print tags_low
        mixset = api.mixset(tags=tags_low, sort='popular')
        urls=search_music_generator(mixset)
        if len(urls) >0 :
            print "http://{}:{}".format(self.ip,self.port)
            server = xmlrpclib.Server("http://{}:{}".format(self.ip,self.port))
            server.init_play_music(json.dumps(urls),tags)
            print urls
            return urls[0]['name'], urls[0]['img_url']
        else :
            print "no url found", "Err"
            return "no url found", "Err"


class Raspi(xmlrpc.XMLRPC):
    def __init__(self):
        self.rpi= list()

    ##############Functions added to communicate with the raspi
    #TODO to be completed/modified
    def xmlrpc_add_raspi(self,ip,port,macAddress):
        print "Adding raspi ip: " + str(ip) + "port: "+ str(port) + "Mac Address: " + macAddress
        id=len(self.rpi)
        self.rpi.append(RaspiUnit(name="rpi"+str(len(self.rpi))))
        self.device_id = 1000 + id
        self.rpi[id].ip=ip
        self.rpi[id].port=int(port)
        self.rpi[id].macAddress=macAddress
        if len(RaspiUnit.objects(name=str(self.rpi[id].name))) == 0 :
            RaspiUnit.objects.create(name=str(self.rpi[id].name), ip=ip, port=port, macAddress=macAddress, device_id = 1000 + id)
        else :
            raspiU = RaspiUnit.objects(name=str(self.rpi[id].name))[0]
            raspiU.device_id = 1000 + id
            raspiU.ip=ip
            raspiU.port=port
            raspiU.macAddress=macAddress
            raspiU.save()
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
            if len(urls) >0 :
                print "http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port)
                server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
                server.init_play_music(json.dumps(urls),tags)
                print urls
                return urls[0]['name'], urls[0]['img_url']
            else :
                return "no url found", "Err"
        else :
            return "Failed, no raspi get this ID" , "Err"


    def xmlrpc_next_music(self, id):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"

            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            next_music = server.next_music()
        else :
            return "Failed, no raspi get this ID"
        return next_music

    def xmlrpc_previous_music(self, id):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return "Failed, no raspi registered at this ID"
            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            previous_music = server.previous_music()
        else :
            return "Failed, no raspi get this ID"
        return previous_music

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

    def xmlrpc_music_playing(self, id):
        if id<len(self.rpi):
            if self.rpi[id].macAddress=="":
                return json.dumps({  'ok' : False, 'result' : "Failed, no raspi get this ID"})
            server = xmlrpclib.Server("http://{}:{}".format(self.rpi[id].ip,self.rpi[id].port))
            result = json.loads(server.music_playing())
        else :
            return json.dumps({  'ok' : False, 'result' : "Failed, no raspi get this ID"})
        return json.dumps({  'ok' : result['ok'], 'result' : result['result']})
        
class RpcServer(xmlrpc.XMLRPC):

    def __init__(self, main_server):
        xmlrpc.XMLRPC.__init__(self)
        self.main_server = main_server

        raspi = Raspi()
        self.putSubHandler('raspi',raspi)

    def xmlrpc_ping(self, msg):
        logger.info("RpcServer.xmlrpc_ping(\"" + str(msg) + "\")")
        return msg

    def xmlrpc_trigger_connection(self, connection_id):
        print connection_id
        connection = Connection.objects.get(id=connection_id)

        if connection is None:
            logger.error("Unknown binding received")
            return False

        try:
            connection.trigger(self.main_server)
            return True
        except Exception as e:
            logger.exception(e)

        return False

    @staticmethod
    def xmlrpc_bind_devices(sensor_id, sensor_event, actuator_id, actuator_callback):
        sensor = devices.Sensor.objects(device_id=sensor_id).first()
        actuator = devices.Actuator.objects(device_id=actuator_id).first()

        if not sensor or not actuator:
            logger.error("Unknown device when binding {}.{} to {}.{}".format(sensor.__class__, sensor_event, actuator.__class__, actuator_callback))
            return

        connection = sensor.events[sensor_event].connect(actuator.callbacks[actuator_callback])

        return connection.id

    """
    def xmlrpc_trigger_event(self, sensor_id, sensor_event):
        sensor = devices.Sensor.objects(device_id=sensor_id).first()

        if not sensor:
            logger.error("Unknown device when triggering {}.{}".format(sensor_id, sensor_event))
            return False

        try:
            getattr(sensor, sensor_event)(self.main_server)
            return True
        except AttributeError as ae:
            logger.error("An error occurred when triggering event {}.{} ".format(sensor.__class__.__name__, sensor_event))
            logger.exception(ae)

        return False
    """

def search_music_generator(mixset):
    urls=[]
    for mix in mixset.mixes[:1]:
        i=0
        try:
            for song in mix:
                if(i<5):
                    urls.append({'name': song.data['name'], 'stream_url' : song.data['track_file_stream_url'], 'img_url': song.data['buy_icon']})# ou track_file_stream_url
                    print song.data['track_file_stream_url']
                    print song.data
                    i+=1
        except requests.HTTPError as err:
            print err
    return urls
