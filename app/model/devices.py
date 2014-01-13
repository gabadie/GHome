#!/usr/bin/env python
# -*- coding: utf-8 -*-

import core
import mongoengine

# Sensors

class Thermometer(object):
    class Reading(core.Reading):
        temperature = mongoengine.FloatField(required=True)
        humidity = mongoengine.FloatField(required=True) 
        
class WindowContact(object):
    open = mongoengine.BooleanField(required=True)

    class Reading(core.Reading):
        opened = mongoengine.BooleanField(required=True)

class Switch(object):
    on = mongoengine.BooleanField(required=True, default=False)

    class Reading(core.Reading):
        turned_on = mongoengine.BooleanField(required=True)

# Actuators

class Lamp(object):
    turned_on = mongoengine.BooleanField(required=True, default=False)
