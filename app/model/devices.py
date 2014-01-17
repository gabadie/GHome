#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import mongoengine
import datetime

# Generic classes

class Device(mongoengine.Document):
    device_id = mongoengine.IntField(required=True, unique=True)
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
    ignored = mongoengine.BooleanField(required=True, default=False)
    actuators = mongoengine.ListField(mongoengine.ReferenceField(Actuator), default=[])

    def activated(self):
        for actuator in self.actuators:
            actuator.activate(self)

# Sensors

class Thermometer(Sensor):
    class Reading(Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True)
        
class WindowContact(Sensor):
    open = mongoengine.BooleanField(required=True)

    class Reading(Reading):
        open = mongoengine.BooleanField(required=True)

class Switch(Sensor):
    top_right = mongoengine.BooleanField(default=False)
    bottom_right = mongoengine.BooleanField(default=False)
    top_left = mongoengine.BooleanField(default=False)
    bottom_left = mongoengine.BooleanField(default=False)

    class Reading(Reading):
        side = mongoengine.IntField(required=True)
        direction = mongoengine.IntField(required=True)
        pressed = mongoengine.BooleanField(required=True)
        
class LightMovementSensor(Sensor):
    class Reading(Reading):
        voltage = mongoengine.FloatField(required=True)
        brightness = mongoengine.FloatField(required=True)
        movement = mongoengine.BooleanField(required=True)

# Actuators

class Lamp(Actuator):
    turned_on = mongoengine.BooleanField(required=True, default=False)
