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

    def xmlrpc_ignore_sensor(self, device_id, ignored):
        if not isinstance(device_id, str):
            return xmlrpc.Fault(1001, "Invalid parameter <device_id>: must be a string.")

        if not isinstance(ignored, bool):
            return xmlrpc.Fault(1002, "Invalid parameter <activate>: must be a boolean.")

        sensor = enocean.devices.Sensor.objects(device_id=device_id).first()

        if not sensor:
            return xmlrpc.Fault(1201, "Invalid operation: Unknown device id.")

        sensor.ignored = ignored
        sensor.save()

        return True

    # TODO : integrate this to create_device ? add tests ?
    def xmlrpc_create_sensor(self, sensor_id, sensor_name, sensor_type, actuators=None):
        if not actuators:
            actuators = []
        actuators = model.core.Actuator.objects(device_id__in=actuators)

        # Finding the sensor class
        SensorClass = [s_class for s_class in enocean.devices.Sensor.__subclasses__() if s_class.__name__ == sensor_type][0]

        # Creating the new device
        s = SensorClass(device_id=sensor_id, name=sensor_name, actuators=actuators, ignored=False)
        s.save()

        return True

    def xmlrpc_remove_device(self, device_id):
        device = model.Device.objects(device_id=device_id).first()
        if device:
            device.delete()
            return True
        else:
            return xmlrpc.Fault(2001, "Incorrect <device_id> value: no device with that id was found.")



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

        # Finding the device class
        DeviceClass = [d_class for d_class in model.core.Device.__subclasses__() if d_class.__name__ == device_type][0]

        d = DeviceClass(device_id=device_id, name=device_name, ignored=False)
        d.save()

        return True

 