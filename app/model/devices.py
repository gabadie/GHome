#!/usr/bin/env python
# -*- coding: utf-8 -*-

 
import mongoengine
import datetime

# Generic classes

class Device(mongoengine.Document):
    device_id = mongoengine.StringField(required=True, unique=True)
    name = mongoengine.StringField()

    meta = {'allow_inheritance': True}

class Reading(mongoengine.Document):
    device = mongoengine.ReferenceField(Device, required=True)
    date = mongoengine.ComplexDateTimeField(default=datetime.datetime.now().strftime("%Y,%m,%d,%H,%M,%S,%f"))

    meta = {'allow_inheritance': True}


class Actuator(Device):

    def activate(self, sensor):
        raise NotImplementedError

class Sensor(Device):
    actuators = mongoengine.ListField(mongoengine.ReferenceField(Actuator), default=[])

    def activated(self):
        for actuator in self.actuators:
            actuator.activate(self)

# Sensors

class Thermometer(object):
    class Reading(Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True) 
        
class WindowContact(object):
    open = mongoengine.BooleanField(required=True)

    class Reading(Reading):
        opened = mongoengine.BooleanField(required=True)

class Switch(object):
    on = mongoengine.BooleanField(required=True, default=False)

    class Reading(Reading):
        turned_on = mongoengine.BooleanField(required=True)
        
class LightMovementSensor(object):
    class Reading(Reading):
        voltage = mongoengine.FloatField(required=True)
        brightness = mongoengine.FloatField(required=True)
        movement = mongoengine.BooleanField(required=True)

# Actuators

class Lamp(object):
    turned_on = mongoengine.BooleanField(required=True, default=False)
        

