#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core
import mongoengine


class Thermometer(object):
    class Reading(core.Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True)
        
        
class WindowContactor(object):
    class Reading(core.Reading):
        open = mongoengine.BooleanField(required=True)

        
class LightMovementSensor(object):
    class Reading(core.Reading):
        voltage = mongoengine.FloatField(required=True)
        brightness = mongoengine.FloatField(required=True)
        movement = mongoengine.BooleanField(required=True)