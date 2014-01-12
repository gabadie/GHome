#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import core


class Sensor(core.Device):
    def add_telegram(self, telegram, server):
        raise NotImplemented


class Thermometer(Sensor):
    class Reading(core.Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True)
        
        
class WindowContact(Sensor):
    class Reading(core.Reading):
        open = mongoengine.BooleanField(required=True)
