#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import datetime


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
