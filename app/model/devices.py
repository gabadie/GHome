#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import datetime
import event

# Generic classes

class Device(event.Object):
    device_id = mongoengine.IntField(required=True, unique=True)
    name = mongoengine.StringField()

    meta = {'allow_inheritance': True}


class Reading(mongoengine.Document):
    device = mongoengine.ReferenceField(Device, required=True)
    date = mongoengine.DateTimeField(default=datetime.datetime.now)

    meta = {'allow_inheritance': True}

    def __repr__(self):
        return '<{Reading} device={}>'.format(self.device)


class NumericReading(Reading):
    value = mongoengine.FloatField(required=True)

    def __repr__(self):
        return '<NumericReading value={} device={}>'.format(self.value, self.device)

class BooleanReading(Reading):
    value = mongoengine.BooleanField(required=True)

    def __repr__(self):
        return '<BooleanReading value={} device={}>'.format(self.value, self.device)

class Actuator(Device):

    def activate(self, sensor):
        raise NotImplementedError

class Sensor(Device):
    ignored = mongoengine.BooleanField(required=True, default=False)
    actuators = mongoengine.ListField(mongoengine.ReferenceField(Actuator), default=[])

    def activated(self):
        for actuator in self.actuators:
            actuator.activate(self)

# Numeric reading

class Temperature(NumericReading):
    pass


class Humidity(NumericReading):
    pass


class Brightness(NumericReading):
    pass


class Voltage(NumericReading):
    pass

# Boolean reading

class SwitchTriggered(BooleanReading):
    pass

class WindowState(BooleanReading):
    pass

class Movement(BooleanReading):
    pass


# Other readings
class SwitchState(Reading):
    side = mongoengine.IntField(required=True)
    direction = mongoengine.IntField(required=True)
    pressed = mongoengine.IntField(required=True)
